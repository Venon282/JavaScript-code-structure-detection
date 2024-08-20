import re
import numpy as np

def GetElements(lines, blocks, singles, ignore=[]):
    """
    Process and identify elements within a list of lines based on defined block and single-line patterns.

    Args:
        lines (list of str): The list of lines to be analyzed.
        blocks (dict): A dictionary defining block types with their corresponding patterns and rules.
                       Each key represents a block type, and the value is a dictionary with the following keys:
                       - 'pattern' (str): The regex pattern to identify the block start.
                       - 'open' (str): The character indicating the start of the block's content.
                       - 'close' (str): The character indicating the end of the block's content.
                       - 'have_args' (bool): Whether the block can contain arguments (e.g., within parentheses).
                       - 'recursive' (bool): Whether the block can be nested within the same block type.
                       - 'is_not_in' (list of str): Block types that cannot contain this block type. (empty = all)
                       - 'is_inside' (list of str): Block types that must contain this block type. (empty = all)
        singles (dict): A dictionary defining single-line types with their corresponding patterns and rules.
                        Each key represents a single-line type, and the value is a dictionary with the following keys:
                        - 'element' (str): The string or pattern to identify the single-line element.
                        - 'position' (str): The expected position of the element (None, 'up', 'down', or 'default').
                        - 'way' (str): The method to verify the element ('==', 'startswith', 'endswith', 'in', or custom).
        ignore (list of str, optional): A list of strings or patterns to ignore during the analysis. Defaults to an empty list.

    Returns:
        list of list: A list of identified elements, where each element is a list containing:
                      - type (str): The type of the element (block or single).
                      - start (int): The start line index of the element.
                      - end (int): The end line index of the element.
                      - name (str or None): The name or identifier of the element, if applicable.
    """
    block_parenthesis = [True, None]    # Permite to know if we are in arguments lines (in_arguments ?, the type)
    blocks_key = list(blocks.keys())    # Get a list of the blocks key
    singles_key = list(singles.keys())  # Get a list of the single elements key

    def Main(lines):
        """
        Main processing function that iterates through lines to identify and categorize elements.

        Args:
            lines (list of str): The list of lines to be processed.

        Returns:
            list of list: A list of identified elements with their type, start index, end index, and name.
        """
        elements = []                               # List that will contain the result (type, start, end, name)

        # in_ Permite to know what block/single is started
        in_ = {key:[] for key in blocks_key}        # For the blocks, we init it with an empty list (each elements = a block start)
        in_.update({key:0 for key in singles_key})  # For the sungle, a simple integer 

        # Track the past types
        prev_type = None
        prev_block_type = None

        for i, line in enumerate(lines):
            # Get the line type
            type_ = DefineType(line, in_)

            # Update the blocks
            elements, in_ = UpdateBlocks(elements, in_, i, line)

            # If the type is defined and (it not have a previous block or the previous block is recursite or the previous block is empty)
            if type_ is not None and (prev_block_type is None or blocks[prev_block_type]['recursive'] is True or len(in_[prev_block_type])==0):
                
                elements, in_ = HandleType(elements, type_, in_, i, line)   # Handle the current detected type 
                in_ = Reinit(in_, type_)                                    # Reinit the single types

                # Update the previous block type if need
                if type_ in blocks_key:
                    prev_block_type = type_
            
            prev_type = type_   # Update the prev type

        return elements


    def UpdateBlocks(elements, in_, i, line):
        """
        Update the status of block elements based on the current line and modify their start/end indexes accordingly.

        Args:
            elements (list of list): The list of currently identified elements.
            in_ (dict): A dictionary tracking the current state of blocks and singles.
            i (int): The current line index being processed.
            line (str): The current line content.

        Returns:
            tuple: Updated elements and state dictionary after processing the current line.
        """
        def Del(list_):
            """
            Delete entries from a list based on specific conditions.

            Args:
                list_ (list of int): A list representing block counts to be potentially modified.

            Returns:
                list of int: The modified list after deletions.
            """
            last = 1
            # For each list elements, get the index where the blocks are end up
            for idx in range(len(list_)):   
                if list_[idx]>0:    # So if >0 (in process), stop there
                    last = idx

            # Reverse it, and delete the indexs of the already process end up
            for idx in sorted(np.arange(last), reverse=True):
                del list_[idx]
            return list_

        def UpdateState(line, nb_open_close, line_idx, type_, blocks, block_idx, in_, nb_blocks_s, elements, update_type):
            """
            Update the state of a block element based on whether it has reached its end or not.

            Args:
                line (str): The line being processed to check for block end conditions.
                nb_open_close (int): The current count of open/close indicators for the block.
                line_idx (int): The current line index being processed.
                type_ (str): The type of the block element being updated.
                blocks (dict): A dictionary defining block types and their characteristics, including open and close patterns.
                block_idx (int): The index of the block in the current state.
                in_ (dict): A dictionary tracking the current state of blocks and single-line elements.
                nb_blocks_s (int): The total number of blocks of this type currently tracked.
                elements (list of list): The list of currently identified elements, including their start and end positions.
                update_type (str): The type of element to update if the current block is not yet finished.

            Returns:
                tuple: Updated elements and state dictionary after processing the current line.
                    - elements (list of list): The updated list of identified elements.
                    - in_ (dict): The updated state dictionary with modified block information.
            """
            is_endup, _ = IsEndUp(line, nb_open_close, add=blocks[type_]['open'], remove=blocks[type_]['close']) # Get the new advancement
            if is_endup is True:                            # If end up
                if block_idx == 0:                          # If it's the oldes block, delete
                    in_[type_][block_idx] = 0
                    in_[type_] = Del(in_[type_])
                else:                                       # If it's not the oldest block, mark it as end up
                    in_[type_][block_idx] = 0
                elements = UpdateLastIndex(elements, type_, line_idx, num=(nb_blocks_s-1)-block_idx)    # Update the elements
            else:                                           # If block not end up update it's advancement
                in_[update_type][block_idx] = is_endup      
            return elements, in_


        line_content = GetNormalizedLine(line)
        
        for type_ in blocks_key:        # For each block types
            n = len(in_[type_])         # Get the numner of process blocks
            for j in range(n-1, -1, -1):# For each of this blocks (starting by the most recent)
                if block_parenthesis[0] is not True and type_ == block_parenthesis[1] and j == n-1:                         # If arguments are started and not end up and it's the last item
                    block_parenthesis[0], idx_e = IsEndUp(line=line_content, n=block_parenthesis[0], add='(', remove=')')   # Check if end up at this line or get the new advancement
                    if block_parenthesis[0] is True:                                                                        # If this time it's end up
                        start_line = line_content[idx_e:]                                                                   # Get the rest of the line after this args
                        elements, in_ = UpdateState(line=start_line, nb_open_close=0, line_idx=i, type_=type_, blocks=blocks, block_idx=j, in_=in_, nb_blocks_s=n, elements=elements, update_type=block_parenthesis[1])
                
                elif in_[type_][j]>0:                                                                                   # If the block is not end up
                    prev = in_[type_][j]                                                                                # Save it's current state
                    elements, in_ = UpdateState(line=line_content, nb_open_close=prev, line_idx=i, type_=type_, blocks=blocks, block_idx=j, in_=in_, nb_blocks_s=n, elements=elements, update_type=type_)

        return elements, in_

    def IsEndUp(line, n, add='{', remove='}'):
        """
        Determine if a line marks the end of a block based on a counter for opening and closing characters.

        Args:
            line (str): The line to be checked.
            n (int): The current count of open block indicators.
            add (str, optional): The character that indicates an opening. Defaults to '{'.
            remove (str, optional): The character that indicates a closing. Defaults to '}'.

        Returns:
            tuple: A boolean indicating if the block ends on this line, and the final index examined.
        """
        have_change = False                     # Bool to know if a change have occur
        size_max = max(len(add), len(remove))   # The size_max between the opening and closing

        # Check the line size
        if len(line)<size_max:
            return n, len(line)

        i = 0
        while i < len(line)-(size_max-1):       # While the end of the line is not reached
            # Get the samples
            sample_add = line[i: i+len(add)]        
            sample_remove = line[i: i+len(remove)]

            if sample_add == add:   # If add
                n+=1                # Add one element
                have_change = True  # have_change is true
                i+=len(add)-1       # pass the len of the add element
            elif sample_remove == remove and n-1>=0:
                n-=1
                have_change = True
                i+=len(remove)-1
            
            # If a change and we are at 0, the end is reach
            if n == 0 and have_change:
                return True, i + size_max - 1

            i+=1    # If no end, pass to the next char
        return n, i # Return the advancement

    def DefineType(line, in_):
        """
        Define the type of the current line (block, single, or none) based on the provided patterns.

        Args:
            line (str): The line to be analyzed.
            in_ (dict): A dictionary tracking the current state of blocks and singles.

        Returns:
            str or None: The identified type of the line or None if no type is matched.
        """
        line_content = GetNormalizedLine(line)

        # Check the single types that need to be check before the blocks
        for type_, values in singles.items():
            if values['position'] == 'up' and VerifyType(string=line_content, element=values['element'], way=values['way']):
                return type_
        
        # Check the blocks types
        for type_, values in blocks.items():
            pattern = values['pattern']
            # If match and not ignore pattern
            if re.search(pattern, line_content) and all(ign not in line_content for ign in ignore): 
                # If the block is in or not in some blocks
                if all(len(in_[no_type])==0 for no_type in blocks[type_]['is_not_in']) and all(len(in_[no_type])>0 for no_type in blocks[type_]['is_inside']):
                    return type_

        # Check the single types that need to be check after the blocks
        for type_, values in singles.items():
            if values['position'] == 'down' and VerifyType(string=line_content, element=values['element'], way=values['way']):
                return type_
        
        # default blocks, not very usefull
        for type_, values in singles.items():
            if values['position'] == 'default':
                return type_

        return None

    def VerifyType(string, element, way):
        """
        Verify if a string matches a specific type based on the defined method.

        Args:
            string (str): The string to be checked.
            element (str): The element or pattern to match against.
            way (str): The method of verification ('==', 'startswith', 'endswith', 'in', or custom).

        Returns:
            bool: True if the string matches the specified method, otherwise False.
        """
        if way == '==':
            return string == element
        elif way == 'startswith':
            return string.startswith(element)
        elif way == 'endswith':
            return string.endswith(element)
        elif way == 'in':
            return string in element
        elif way.startswith('no '):
            new_way = way[3:].split(',')
            return all(char not in string for char in new_way[3:])
        else:
            raise Exception(f'The way {way} is not handle.')

    def UpdateLastIndex(elements, type_, new_idx, num=0):
        """
        Update the end index of the last occurrence of a specific element type.

        Args:
            elements (list of list): The list of currently identified elements.
            type_ (str): The type of element to be updated.
            new_idx (int): The new end index for the element.
            num (int, optional): The specific occurrence to update if there are multiple. Defaults to 0.

        Returns:
            list of list: The updated list of elements with modified end indexes.
        """
        found = False   # Verify if the target as been found
        count = 0       # The number of occurence until reach the num desire

        for j in range(len(elements)-1, -1, -1):    # For each elements (reverse order)
            if elements[j][0] == type_:             # If it's the desire type
                if count == num:                    # And it's the desire num
                    elements[j][2] = new_idx        # Update its index
                    found = True                    # Found to true
                    break                           # Stop the process
                else:                               # If it's not the good num
                    count +=1                       # Just continue until found it
                
        # Error if element not found
        if found is False:
            raise Exception('End block comments detected line ', i, ' but no start found.')

        return elements

    def HandleType(elements, type_, in_, i, line):
        """
        Handle the processing of a specific type by updating elements and state based on the line.

        Args:
            elements (list of list): The list of currently identified elements.
            type_ (str): The type of element being processed.
            in_ (dict): A dictionary tracking the current state of blocks and singles.
            i (int): The current line index being processed.
            line (str): The current line content.

        Returns:
            tuple: Updated elements and state dictionary after processing the current line.
        """
        line_content = GetNormalizedLine(line)

        # If the element is a single line
        if type_ in singles_key:
            # If it's the first one, add it
            if in_[type_] == 0:
                elements.append([type_, i, i,  None])
                in_[type_] += 1
            # If it make more than a line with this type, update the last occurence
            else:
                elements[-1][2] = i
        
        # If it's a block
        elif type_ in blocks_key:
            n_parenthesis, idx_e = IsEndUp(line=line_content, n=0, add='(', remove=')') # Init the parenthesis

            # If have args, add the args detection
            if blocks[type_]['have_args']:
                block_parenthesis[0] = n_parenthesis
            # If not, ignore it
            else:
                block_parenthesis[0] = True
                idx_e = 0

            block_parenthesis[1] = type_

            if block_parenthesis[0] is True:        # If no args or args end up
                start_line = line_content[idx_e:]   # Get the line without and update the block state
                is_endup, idx_e = IsEndUp(line=start_line, n=0, add=blocks[type_]['open'], remove=blocks[type_]['close'])

                # If the block is not end up, we add it to the process one
                if is_endup is not True:
                    in_[type_].append(is_endup)

            # If the args are not end up, current block process is at 0 (but not end up)
            else:
                in_[type_].append(0)

            elements.append([type_, i, i,  GetName(type_, line_content)]) # Add the new block elements

        return elements, in_

    def GetName(type_, line):
        """
        Extract the name or identifier of a block element from the line using its defined pattern.

        Args:
            type_ (str): The type of the block element.
            line (str): The line content to extract the name from.

        Returns:
            str or None: The extracted name or None if no name is found.
        """
        match = re.search(blocks[type_]['pattern'], line)

        if match:
            name = match.group(1) if len(match.groups()) >0 else None
            return name if name is not None else ''
        else:
            return None

    def Reinit(in_, type_):
        """
        Reinitialize the state of single-line elements, setting their counters to zero except for the current type.

        Args:
            in_ (dict): The current state dictionary.
            type_ (str): The type that should not be reset.

        Returns:
            dict: The reinitialized state dictionary.
        """
        for single in singles_key:
            if type_ != single:
                in_[single] = 0

        return in_

    return Main(lines)

def DisplayElements(elements):
    """
    Print each element from the list of identified elements.

    Args:
        elements (list of list)
    
    Returns:
        None: This function does not return any value. It prints the elements to the standard output.
    """
    for element in elements:
        print(element)

def GetNormalizedLine(line):
    """
    Normalize a line by removing quoted substrings and extra whitespace.

    Args:
        line (str): The line of text to be normalized.

    Returns:
        str: The normalized line with quoted substrings removed and whitespace reduced to single spaces.
    """
    normalized_line = re.sub(r"'[^']*'|\"[^\"]*\"", "", line)

    normalized_line = ' '.join(normalized_line.split()).strip()
    
    return normalized_line