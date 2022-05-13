const express = require("express");
const router = express.Router();
const { register, login, deleteUser, getUsers, tryAdminAccess } = require("./auth");
const { adminAuth } = require("../middleware/auth");

router.route("/register").post(adminAuth, register);
router.route("/login").post(login);
router.route("/deleteUser").delete(adminAuth, deleteUser);
router.route("/getUsers").get(adminAuth, getUsers);
router.route("/tryAdminAccess").get(adminAuth, tryAdminAccess);

module.exports = router;
