const UserSchema = require("../model/User");
const users = require('../data/userDB.json');
const Ajv = require("ajv");
const ajv = new Ajv();
const bcrypt = require('bcrypt');
const fs = require('fs');
const jwt = require("jsonwebtoken");
const path = require("path");

const validate = ajv.compile(UserSchema);
const jwtSecret = '5ab67fbe236d1025a9b52b6179a8db6dca16a4d0a4a843c86c09535feb0ddaddc82f8b';

exports.register = async (req, res, next) => {
  let { username, password } = req.body;
  let role = req.body.role;
  if (!role) {
    role = "Basic";
  }

  try {
    if(password && password.length < 6) {
      return res.status(400).json({message: "Password less than 6 characters;"});
    }

    const user = {
      username,
      password,
      role
    }

    if (validate(user)) {
      for (var i = 0; i < users.length; i++) {
        if (username === users[i].username) {
          return res.status(405).json({message: "User already exists"});
        }
      }

      password = await bcrypt.hash(password, 10);

      user.password = password;
      users.push(user);

      fs.writeFileSync(path.join(__dirname,'../data/userDB.json'), JSON.stringify(users));

      return res.status(201).json({
        message: "User successfully created"
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

  console.log(users.length);
  try {
    let foundUser = false;
    for (var i = 0; i < users.length; i++) {
      console.log(username + " " + users[i].username);
      if (username === users[i].username && bcrypt.compareSync(password, users[i].password)) {
        foundUser = true;
        console.log(user);
        user.role = users[i].role;
        break;
      }
    }

    if (!foundUser) {
      return res.status(401).json({message: "Login failed", error: "User not found."});
    }
    else {
      // jwt token
      const maxAge = 60 * 60; // 60s * 60 = 1h
      const token = jwt.sign(
        { id: user.username, role: user.role },
        jwtSecret,
        { expiresIn: maxAge }
      );

      res.cookie("jwt", token, {
        secure: true,
        httpOnly: true,
        maxAge: maxAge * 1000 // 1h in ms
      });

      return res.status(200).json({message: "Login successful"});
    }
  } catch (e) {
    res.status(400).json({
      message: "An error occured",
      error: error.message,
    });
  }
};

exports.deleteUser = async (req, res, next) => {
  const username = req.body.username;
  if (username === undefined) {
      return res.status(400).json({message: "No User specified"});
  }

  for (var i = 0; i < users.length; i++) {
    if (username === users[i].username) {
      users.splice(i, 1);
      try {
        fs.writeFileSync(path.join(__dirname,'../data/userDB.json'), JSON.stringify(users));
      } catch (e) {
        console.log(e);
        res.status(400).json({
          message: "An error occured",
          error: error.message,
        });
      }

      return res.status(200).json({message: "User deleted", username});
    }
  }

  return res.status(400).json({message: "User not found", username});
};

exports.getUsers = async (req, res, next) => {
  const currentUsers = [];
  for (var i = 0; i < users.length; i++) {
    currentUsers[i] = {"username": users[i].username, "role": users[i].role}
  }

  res.status(200).json({
    message: "Registered Users",
    currentUsers,
  });
};

exports.tryAdminAccess = async (req, res, next) => {
  res.status(200);
}
