const express = require("express");
const router = express.Router();
const { register, login, deleteUser } = require("./auth");
const { adminAuth } = require("../middleware/auth");

router.route("/register").post(adminAuth, register);
router.route("/login").post(login);
router.route("/deleteUser").delete(adminAuth, deleteUser);

module.exports = router;
