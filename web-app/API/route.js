const express = require("express");
const router = express.Router();
const { getVideoNames, getVideo } = require("./videoApi");
const { userAuth } = require("../middleware/auth.js");

router.route("/getVideoNames").get(userAuth, getVideoNames);
router.route("/getVideo").get(userAuth, getVideo);

module.exports = router;
