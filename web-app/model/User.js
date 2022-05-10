const UserSchema = {
  type: "object",
  properties: {
    username: {type: "string", minLength: 4},
    password: {type: "string", minLength: 6},
    role: {type: "string"}
  },
  required: ["username", "password", "role"],
}

module.exports = UserSchema;
