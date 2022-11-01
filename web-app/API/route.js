const express = require("express");
const router = express.Router();
const { getVideoNames } = require("./videoApi");
const { userAuth } = require("../middleware/auth.js");

router.route("/getVideoNames").get(userAuth, getVideoNames);

module.exports = router;
