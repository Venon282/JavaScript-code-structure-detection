# JavaScript-code-structure-detection
Permite to detect the differents elements in a JavaScript code. Start and end of the function, functions arrow, comments, etc

## How to use
Call the GetElements function

## Pros
- Allow you to use it for recursion after (cf my repo "JavaScript sort and classify your code"

## Cons
- It need a minimal indentation as it's process by lines

## Warning
- The order of elements in blocks and single have an importance.
    - It's better to have the block comment in first
    - To have the method block before the function_call
    - etc

## Exemple
```python
singles = {
    'comment':{
        'element':'//',
        'way':'startswith',
        'position':'up'
    },
    'empty':{
        'element':'',
        'way':'==',
        'position':'up'
    },
    'import':{
        'element':'import',
        'way':'startswith',
        'position':'up'
    },
    'export':{
        'element':'export',
        'way':'startswith',
        'position':'down'
    },
    'other':{
        'element':'',
        'way':'no (,),{,},/*,*/',
        'position':'down'
    },
    'default':{
        'element':'',
        'way':'',
        'position':'default'
    },
}
```

```python
blocks = {
    'comment_block':{
        'pattern': r'\/\*',
        'have_args':False,
        'is_inside':[],
        'is_not_in':['comment_block'],
        'recursive':False,
        'open':'/*',
        'close':'*/',
    },
    'class':{
        'pattern': r'\bclass(?:\s+(\w*))?\b',   # Pattern for identify the start of the block
        'have_args':False,                      # If args, open and close start once parenthesis close # todo improve it (veryfy if something open before the open char. If the case wait it to close)
        'is_inside':[],                         # It is present in others defined blocks ? (Empty = all allow)
        'is_not_in':['comment_block'],          # It can't be present in some defined blocks ? (Empty = all allow)
        'recursive':True,                       # Do we want it's content be process ?
        'open':'{',                             # str that open the block
        'close':'}',
    },
    'function':{
        'pattern': r'\bfunction\s+(\w+)\s*\(', 
        'have_args':True,
        'is_inside':[],
        'is_not_in':['comment_block'],
        'recursive':True,
        'open':'{',
        'close':'}',
    },
    'function_arrow':{
        'pattern': r'\bconst\s+\(\s*(\w+)\s*=\s*\([^)]*\)\s*=>\s*',
        'have_args':False,
        'is_inside':[],
        'is_not_in':['comment_block'],
        'recursive':True,
        'open':'(',
        'close':')',
    },
    'function_arrow_':{
        'pattern': r'\bconst\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*',
        'have_args':False,
        'is_inside':[],
        'is_not_in':['comment_block'],
        'recursive':True,
        'open':'{',
        'close':'}',
    },
    'methods':{
        'pattern': r'\b(\w+)\s*\([^)]*\)\s*',
        'have_args':True,
        'is_inside':['class'],
        'is_not_in':['methods', 'function', 'function_arrow', 'comment_block', 'function_call', 'other_multi'],
        'recursive':False,
        'open':'{',
        'close':'}',
    },
    'other_multi':{
        'pattern': r'\b.*\{',
        'have_args':False,
        'is_inside':[],
        'is_not_in':['comment_block'],
        'recursive':False,
        'open':'{',
        'close':'}',
    },
    'function_call':{
        'pattern': r'\b\w+\s*\(+',
        'have_args':False,
        'is_inside':[],
        'is_not_in':['comment_block'],
        'recursive':False,
        'open':'(',
        'close':')',
    }, 
}
```

## Output exemple
type, start, end, name
```
['import', 0, 2, None]
['empty', 3, 3, None]
['comment_block', 4, 6, '']
['default', 6, 6, None]
['class', 7, 40, 'VictoryList']
['methods', 8, 10, 'constructor']       
['default', 10, 10, None]
['comment_block', 11, 13, '']
['default', 13, 13, None]
['methods', 14, 25, 'addVictory']       
['default', 25, 25, None]
['empty', 26, 26, None]
['comment_block', 27, 29, '']
['default', 29, 29, None]
['methods', 30, 32, 'getTotalVictories']
['default', 32, 32, None]
['empty', 33, 33, None]
['comment_block', 34, 36, '']
['default', 36, 36, None]
['methods', 37, 39, 'removeLastVictory']
['default', 39, 40, None]
['empty', 41, 41, None]
['comment_block', 42, 44, '']
['default', 44, 44, None]
['class', 45, 70, 'ChampionCalculator']
['methods', 46, 48, 'constructor']
['default', 48, 48, None]
['empty', 49, 49, None]
['comment_block', 50, 52, '']
['default', 52, 52, None]
['methods', 53, 55, 'isChampion']
['default', 55, 55, None]
['empty', 56, 56, None]
['comment_block', 57, 59, '']
['default', 59, 59, None]
['methods', 60, 62, 'multiplyByFactor']
['default', 62, 62, None]
['empty', 63, 63, None]
['comment_block', 64, 66, '']
['default', 66, 66, None]
['methods', 67, 69, 'addVictoryPoints']
['default', 69, 70, None]
['empty', 71, 71, None]
['comment_block', 72, 74, '']
['default', 74, 74, None]
['empty', 75, 75, None]
['class', 76, 101, 'Hero']
['methods', 77, 79, 'constructor']
['default', 79, 79, None]
['empty', 80, 80, None]
['comment_block', 81, 83, '']
['default', 83, 83, None]
['methods', 84, 86, 'greetHero']
['default', 86, 86, None]
['empty', 87, 87, None]
['comment_block', 88, 90, '']
['default', 90, 90, None]
['methods', 91, 93, 'getHeroNameLength']
['default', 93, 93, None]
['empty', 94, 94, None]
['comment_block', 95, 97, '']
['default', 97, 97, None]
['methods', 98, 100, 'makeHeroNameUppercase']
['default', 100, 101, None]
['empty', 102, 102, None]
['export', 103, 103, None]
['empty', 104, 104, None]
```

The code :
```js
import React from 'react'; 
import Component1 from './Component1';
import Component2 from './Component2';

/*
This is the VictoryList class that manages a list of items
*/
export class VictoryList {
    constructor(items = []) {
        this.items = items;
    }
    /*
    This method adds a new item to the list
    */
    addVictory(item) {
        this.items.push(item);
        if (item === 3) {
            return 2; // Special victory condition
        } else if (item === 5) {
            return 9; // Another special victory condition
        }

        for (let i = 0; i < 5; i++) {
            console.log(i); // Victory parade
        }
    }

    /*
    This method returns the total number of victories
    */
    getTotalVictories() {
        return this.items.length;
    }

    /*
    This method removes the last victory from the list
    */
    removeLastVictory() {
        return this.items.pop();
    }
}

/*
This is the ChampionCalculator class that performs calculations
*/
export class ChampionCalculator {
    constructor(number) {
        this.number = number;
    }

    /*
    This method checks if the number is a champion (even)
    */
    isChampion() {
        return this.number % 2 === 0;
    }

    /*
    This method multiplies the number by a victory factor
    */
    multiplyByFactor(factor) {
        return this.number * factor;
    }

    /*
    This method adds a victory value to the number
    */
    addVictoryPoints(value) {
        return this.number + value;
    }
}

/*
This is the Hero class that handles basic operations
*/

class Hero {
    constructor(name) {
        this.name = name;
    }

    /*
    This method logs a heroic greeting message
    */
    greetHero() {
        console.log(`Greetings, Hero ${this.name}!`);
    }

    /*
    This method returns the length of the hero's name
    */
    getHeroNameLength() {
        return this.name.length;
    }

    /*
    This method converts the hero's name to uppercase
    */
    makeHeroNameUppercase() {
        return this.name.toUpperCase();
    }
}

export default Hero;
```


