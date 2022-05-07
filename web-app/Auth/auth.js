const UserSchema = require("../model/User");
const Ajv = require("ajv");
const ajv = new Ajv();

exports.register = async (req, res, next) => {
  const { username, password } = req.body;
  if(password.length < 6) {
    return res.status(400).json({message: "Password less than 6 characters;"});
  }

  try {
    const user = {
      username,
      password,
    }

    res.status(200).json({
      message: "User successfully created",
      user,
    });
  } catch (err) {
    res.status(401).json({
      message: "User not successfully created",
      error: error.message,
    });
  }
};
