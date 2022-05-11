const UserSchema = require("../model/User");
const users = require('../data/userDB.json');
const Ajv = require("ajv");
const ajv = new Ajv();
const bcrypt = require('bcrypt');
const fs = require('fs');

const validate = ajv.compile(UserSchema);

exports.register = async (req, res, next) => {
  let { username, password } = req.body;

  try {
    if(password != undefined && password.length < 6) {
      return res.status(400).json({message: "Password less than 6 characters;"});
    }

    const role = "Basic";

    const user = {
      username,
      password,
      role
    }

    if (validate(user)) {
      for (var i = 0; i < users.length; i++) {
        if (bcrypt.compareSync(username, users[i].username)) {
          return res.status(405).json({message: "User already exists"});
        }
      }

      password = await bcrypt.hash(password, 10);
      username = await bcrypt.hash(username, 10);

      user.username = username;
      user.password = password;
      users.push(user);

      fs.writeFileSync('C:/Users/janni/github/sysadmin/web-app/data/userDB.json', JSON.stringify(users));
      return res.status(200).json({
        message: "User successfully created",
        user,
      });
    }

    return res.status(400).json({message: "Request Denied", error: "Request contains errors."});
  } catch (err) {
    console.log(err);
    res.status(400).json({
      message: "An error occured. User was not created",
      error: error.message,
    });
  }
};

exports.login = async (req, res, next) => {
  let { username, password } = req.body;
  const role = "";
  const user = {
    username,
    password,
    role
  }

  if (!validate(user)) {
    return res.status(400).json({message: "Request Denied", error: "Request contains errors."});
  }

  try {
    let foundUser = false;
    for (var i = 0; i < users.length; i++) {
      if (bcrypt.compareSync(username, users[i].username) && bcrypt.compareSync(password, users[i].password)) {
        foundUser = true;
        user.role = users[i].role;
        break;
      }
    }

    if (!foundUser) {
      return res.status(401).json({message: "Login failed", error: "User not found."});
    }
    else {
      return res.status(200).json({message: "Login successful", user});
    }
  } catch (e) {
    res.status(400).json({
      message: "An error occured",
      error: error.message,
    });
  }
}
