const UserSchema = require("../model/User");
const users = require('../data/userDB.json');
const Ajv = require("ajv");
const ajv = new Ajv();
const bcrypt = require('bcrypt');
const fs = require('fs');
const jwt = require("jsonwebtoken");
const path = require("path");
const validator = require('validator');

const validate = ajv.compile(UserSchema);
const jwtSecret = '5ab67fbe236d1025a9b52b6179a8db6dca16a4d0a4a843c86c09535feb0ddaddc82f8b';

function validateInput(input) {
  if(validator.contains(input, '>') || validator.contains(input, '<') ||
  validator.contains(input, '&') || validator.contains(input, '\'') || validator.contains(input, '\"') || validator.contains(input, '/')) {
    return false;
  }

  return true;
}

exports.register = async (req, res, next) => {
  const fileBuffer = fs.readFileSync(path.join(__dirname,'../data/userDB.json'));
  const hashedValue = fs.readFileSync(path.join(__dirname,'../data/hash.txt'));
  if (!bcrypt.compareSync(fileBuffer.toString(), hashedValue.toString())) {
    console.log("Register: Detected UserDB Unauthorized modification.");
    return res.status(401).json({message: "User Authentication compromissed"});
  }

  let { username, password } = req.body;
  let role = req.body.role;

  // sanitize
  username = validator.trim(username);
  if (!validateInput(username)) {
    console.log("Register Request: Username contains forbidden characters.");
    return res.status(400).json({message: "User not created: ", error: "Username contains forbidden characters: < > & \' \" or /"});
  }

  password = validator.trim(password);
  if (!validateInput(password)) {
    console.log("Register Request: Password contains forbidden characters.");
    return res.status(400).json({message: "User not created: ", error: "Password contains forbidden characters: < > & \' \" or /"});
  }

  role = validator.trim(role);
  if (!validateInput(role)) {
    console.log("Register Request: Role contains forbidden characters.");
    return res.status(400).json({message: "User not created: ", error: "Userrole contains forbidden characters: < > & \' \" or /"});
  }

  if (!role) {
    role = "Basic";
  }

  console.log("Register Request: Username: " + username);

  try {
    if(password && password.length < 6) {
      console.log("Register Request: Username: " + username + " failed.");
      return res.status(400).json({message: "Password needs at least 6 characters;"});
    }

    const user = {
      username,
      password,
      role
    };

    if (validate(user)) {
      for (var i = 0; i < users.length; i++) {
        if (username === users[i].username) {
          console.log("Register Request: Username: " + username + " failed.");
          return res.status(405).json({message: "User already exists"});
        }
      }

      password = await bcrypt.hash(password, 10);

      user.password = password;
      users.push(user);

      fs.writeFileSync(path.join(__dirname,'../data/userDB.json'), JSON.stringify(users));

      const fileBuffer = fs.readFileSync(path.join(__dirname,'../data/userDB.json'));
      const hashSum = bcrypt.hashSync(fileBuffer.toString(), 10);
      fs.writeFileSync(path.join(__dirname,'../data/hash.txt'), hashSum.toString());

      console.log("Register Request: Username: " + username + " successful.");
      return res.status(201).json({
        message: "User successfully created"
      });
    }

    return res.status(400).json({message: "Request Denied", error: "Request contains errors."});
  } catch (err) {
    console.log("Register: " + err);
    res.status(400).json({
      message: "An error occured. User was not created"
    });
  }
};

exports.login = async (req, res, next) => {
  const fileBuffer = fs.readFileSync(path.join(__dirname,'../data/userDB.json'));
  const hashedValue = fs.readFileSync(path.join(__dirname,'../data/hash.txt'));
  if (!bcrypt.compareSync(fileBuffer.toString(), hashedValue.toString())) {
    console.log("Login: Detected UserDB Unauthorized modification.");
    return res.status(401).json({message: "User Authentication compromissed"});
  }

  let { username, password } = req.body;
  let role = "";

  // sanitize
  username = validator.trim(username);
  if (!validateInput(username)) {
    console.log("Login Request: Username contains forbidden characters.");
    return res.status(400).json({message: "Login failed: ", error: "Username contains forbidden characters: < > & \' \" or /"});
  }

  password = validator.trim(password);
  if (!validateInput(password)) {
    console.log("Login Request: Password contains forbidden characters.");
    return res.status(400).json({message: "Login failed: ", error: "Password contains forbidden characters: < > & \' \" or /"});
  }

  role = validator.trim(role);
  if (!validateInput(role)) {
    console.log("Login Request: Role contains forbidden characters.");
    return res.status(400).json({message: "Login failed: ", error: "Userrole contains forbidden characters: < > & \' \" or /"});
  }

  console.log("Login Request: Username: " + username);
  const user = {
    username,
    password,
    role
  };

  if (!validate(user)) {
    console.log("Login Request: Username: " + username + " failed.");
    return res.status(400).json({message: "Request Denied", error: "Request contains errors."});
  }

  try {
    let foundUser = false;
    for (var i = 0; i < users.length; i++) {
      if (username === users[i].username && bcrypt.compareSync(password, users[i].password)) {
        foundUser = true;
        user.role = users[i].role;
        break;
      }
    }

    if (!foundUser) {
      console.log("Login Request: Username: " + username + " failed.");
      return res.status(401).json({message: "Login failed", error: "Wrong Username or Password"});
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

      console.log("Login Request: Username: " + username + " successful.");
      return res.status(200).json({message: "Login successful"});
    }
  } catch (e) {
    console.log("Login: " + e);
    res.status(400).json({
      message: "An error occured"
    });
  }
};

exports.deleteUser = async (req, res, next) => {
  const fileBuffer = fs.readFileSync(path.join(__dirname,'../data/userDB.json'));
  const hashedValue = fs.readFileSync(path.join(__dirname,'../data/hash.txt'));
  if (!bcrypt.compareSync(fileBuffer.toString(), hashedValue.toString())) {
    console.log("DeleteUser: Detected UserDB Unauthorized modification.");
    return res.status(401).json({message: "User Authentication compromissed"});
  }

  let username = req.body.username;
  if (username === undefined) {
      console.log("DeleteUser Request: No User specified");
      return res.status(400).json({message: "No User specified"});
  }

  // sanitize
  username = validator.trim(username);
  if (!validateInput(username)) {
    console.log("DeleteUser Request: Username contains forbidden characters.");
    return res.status(400).json({message: "User not deleted: ", error: "Username contains forbidden characters: < > & \' \" or /"});
  }

  console.log("DeleteUser Request: Username: " + username);

  for (var i = 0; i < users.length; i++) {
    if (username === users[i].username) {
      users.splice(i, 1);
      try {
        fs.writeFileSync(path.join(__dirname,'../data/userDB.json'), JSON.stringify(users));
      } catch (e) {
        console.log("DeleteUser: " + e);
        res.status(400).json({
          message: "An error occured",
          error: error.message,
        });
      }

      const fileBuffer = fs.readFileSync(path.join(__dirname,'../data/userDB.json'));
      const hashSum = bcrypt.hashSync(fileBuffer.toString(), 10);
      fs.writeFileSync(path.join(__dirname,'../data/hash.txt'), hashSum.toString());
      console.log("DeleteUser Request: Username: " + username + " successful");
      return res.status(200).json({message: "User deleted", username});
    }
  }

  console.log("DeleteUser Request: Username: " + username + " failed");
  return res.status(400).json({message: "User not found", username});
};

exports.getUsers = async (req, res, next) => {
  const fileBuffer = fs.readFileSync(path.join(__dirname,'../data/userDB.json'));
  const hashedValue = fs.readFileSync(path.join(__dirname,'../data/hash.txt'));
  if (!bcrypt.compareSync(fileBuffer.toString(), hashedValue.toString())) {
    console.log("GetUsers: Detected UserDB Unauthorized modification.");
    return res.status(401).json({message: "User Authentication compromissed"});
  }

  const currentUsers = [];
  for (var i = 0; i < users.length; i++) {
    currentUsers[i] = {"username": validator.unescape(users[i].username), "role": validator.unescape(users[i].role)};
  }

  console.log("GetUsers Request: successful");
  res.status(200).json({
    message: "Registered Users",
    currentUsers,
  });
};

exports.tryAdminAccess = async (req, res, next) => {
  res.status(200);
};
