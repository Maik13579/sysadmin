const UserSchema = {
  type: "object",
  required: ["username", "password", "role"],
  properties: {
    username: {type: String, minlength: 4},
    password: {type: String, minlength: 6},
    role: {type: String}
  }
}

module.exports = UserSchema;
