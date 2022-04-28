const bcrypt = require('bcrypt');
const userJson = require('./data/userDB.json');
const fs = require('fs');

function loadUsers() {
  return userJson;
}

async function saveUser() {
  try {
    let paswd = await bcrypt.hash("123", 10);
    let email = await bcrypt.hash("jannik@123.de", 10);
    let user = {
      email: email,
      password: paswd
    };
    let users = [user];

    //todo: change path
    fs.writeFileSync('C:/Users/janni/github/sysadmin/web-app/data/userDB.json', JSON.stringify(users));
    return 1;
  } catch (e) {
    console.log("saving file failed");
    return 0;
  }
}

module.exports.saveUser = saveUser;
module.exports.loadUsers = loadUsers;
