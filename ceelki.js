const fs = require("fs");

const readLines = file => (
    fs.readFileSync(file)
      .toString(`UTF8`)
      .split(`\n`)
); const content = readLines(`./pylog`);


let sIndex, eIndex;
let iterators = [];
content.forEach((c, index) => {
    if(c.includes(`exemption: {`)) sIndex = index;
    if(c.includes(`}`)) {
        eIndex = index;
        iterators.push({sIndex, eIndex});
    }
});


const blocks = [];
iterators.forEach(it => {
    const segment = [];
    for(let i = it.sIndex; i <= it.eIndex; i++)
        segment.push(content[i]);

    blocks.push(segment);
});


blocks.sort();
const accounts = [];

blocks.forEach((block, index) => {
    block.forEach(b => {
        if(b.includes(`account: `)) {
            const accPos = block.indexOf(b);
            block.splice(accPos, 1);

            accounts.push(b);
        }
    });
});


const unique = [];
for(let i = 1; i <= blocks.length; i++) {
    if(JSON.stringify(blocks[i]) === JSON.stringify(blocks[i-1])) {
        if(unique.length <= 0) {
            blocks[i-1].splice(blocks[i-1].length-2, 0, accounts[i-1]);
            unique.push(blocks[i-1]);
        } else {
            unique[unique.length-1].splice(unique.length-3, 0, accounts[i-1]);
            // blocks[i-1].splice(blocks[i-1].length-2, 0, accounts[i-1]);
            // blocks[i].splice(blocks[i].length-2, 0, accounts[i]);


            // W ten else idą konta, które są z nadmiarowych bloków, które już zostały skonsolidowane
            // Aktualnie to prawie działa, ale wrzuca je w zły blok
            // Na razie nie mam pomysłu, jak to rozwiązać
            // Oczywiście całość jest do przepisania, to nie jest dobrej jakości kod XD
            // Jakieś .map(), .filter() i reduce() by tu pasowało wrzucić
            // Ale jeśli to będzie przepisane na Pythona, to nie widzę sensu się spuszczać nad tym kodem
        }
    } else {
        blocks[i-1].splice(blocks[i-1].length-2, 0, accounts[i-1]);
        unique.push(blocks[i-1]);
    }
} 

console.log("\n");
console.log('\x1b[96m ------------------------------  IAM-AP CONSOLIDATION  ------------------------------- \x1b[0m');

// console.log(unique.toString().replace(',', '\n'));

unique.forEach(unq => {
  unq.forEach(u => {
    if(u.includes("exemption")) {console.log(`\x1b[91m ${u} \x1b[0m`);}
    else if(u.includes("account")) {console.log(`\x1b[93m${u} \x1b[0m`);}
    else if(u.includes("}")) {console.log(`\x1b[91m${u} \x1b[0m`);}
    else console.log(u);
  }); console.log(`\n`);
});