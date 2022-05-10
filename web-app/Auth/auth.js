const UserSchema = require("../model/User");
const Ajv = require("ajv");
const ajv = new Ajv();
const bcrypt = require('bcrypt');
const fs = require('fs');

exports.register = async (req, res, next) => {
  let { username, password } = req.body;

  try {
    if(password != undefined && password.length < 6) {
      return res.status(400).json({message: "Password less than 6 characters;"});
    }

    const validate = ajv.compile(UserSchema);
    const role = "Basic";

    const user = {
      username,
      password,
      role
    }

    if (validate(user)) {
      password = await bcrypt.hash(password, 10);
      username = await bcrypt.hash(username, 10);

      user.username = username;
      user.password = password;

// TODO: get all users. check if user already exists. if not then add this user to current users
      fs.writeFileSync('C:/Users/janni/github/sysadmin/web-app/data/userDB.json', JSON.stringify(user));
      return res.status(200).json({
        message: "User successfully created",
        user,
      });
    }

    return res.status(405).json({message: "Request denied"});
  } catch (err) {
    console.log(err);
    res.status(401).json({
      message: "User not successfully created",
      error: error.message,
    });
  }
};
