const express = require("express");
const router = express.Router();
const { register, login, deleteUser, getUsers, tryAdminAccess } = require("./auth");
const { adminAuth } = require("../middleware/auth.js");
const limiter = require("../middleware/rateLimiter.js");
const csrfProtection = require("../middleware/csrfProtection.js");

router.route("/register").post(adminAuth, csrfProtection, register);
router.route("/login").post(limiter, csrfProtection, login);
router.route("/deleteUser").delete(adminAuth, csrfProtection, deleteUser);
router.route("/getUsers").get(adminAuth, getUsers);
router.route("/tryAdminAccess").get(adminAuth, tryAdminAccess);

module.exports = router;
