// Import the "fs" module for reading files
const fs = require("fs");

// Define a function to read a file and split its contents into an array of lines
const readLines = file => (
    fs.readFileSync(file)
      .toString(`UTF8`)
      .split(`\n`)
);

// Read the contents of the "pylog" file into an array of lines
const content = readLines(`./pylog`);

// Define variables to keep track of the start and end indices of each exemption block
let sIndex, eIndex;

// Define an array to store the start and end indices of each exemption block
let iterators = [];

// Loop through the lines of the file and find the start and end indices of each exemption block
content.forEach((c, index) => {
    if(c.includes(`exemption: {`)) sIndex = index;
    if(c.includes(`}`)) {
        eIndex = index;
        iterators.push({sIndex, eIndex});
    }
});

// Define an array to store the contents of each exemption block
const blocks = [];

// Loop through the start and end indices of each exemption block and extract the contents of each block
iterators.forEach(it => {
    const segment = [];
    for(let i = it.sIndex; i <= it.eIndex; i++)
        segment.push(content[i]);

    blocks.push(segment);
});

// Sort the exemption blocks alphabetically
blocks.sort();

// Define an array to store the account information for each exemption block
const accounts = [];

// Loop through each exemption block and extract the account information
blocks.forEach((block, index) => {
    block.forEach(b => {
        if(b.includes(`account: `)) {
            const accPos = block.indexOf(b);
            block.splice(accPos, 1);

            accounts.push(b);
        }
    });
});

// Define an array to store the unique exemption blocks
const unique = [];

// Loop through each exemption block and check if it is a duplicate
for(let i = 1; i <= blocks.length; i++) {
    if(JSON.stringify(blocks[i]) === JSON.stringify(blocks[i-1])) {
        // If the block is a duplicate, add the account information to the previous unique block
        if(unique.length <= 0) {
            blocks[i-1].splice(blocks[i-1].length-2, 0, accounts[i-1]);
            unique.push(blocks[i-1]);
        } else {
            unique[unique.length-1].splice(unique.length-3, 0, accounts[i-1]);
        }
    } else {
        // If the block is not a duplicate, add it to the list of unique blocks
        blocks[i-1].splice(blocks[i-1].length-2, 0, accounts[i-1]);
        unique.push(blocks[i-1]);
    }
} 

// Print the consolidated exemption blocks and account information to the console
console.log("\n");
console.log('\x1b[96m ------------------------------  IAM-AP CONSOLIDATION  ------------------------------- \x1b[0m');

unique.forEach(unq => {
  unq.forEach(u => {
    if(u.includes("exemption")) {console.log(`\x1b[91m ${u} \x1b[0m`);}
    else if(u.includes("account")) {console.log(`\x1b[93m${u} \x1b[0m`);}
    else if(u.includes("}")) {console.log(`\x1b[91m${u} \x1b[0m`);}
    else console.log(u);
  }); console.log(`\n`);
});
