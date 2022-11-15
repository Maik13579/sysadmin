const express = require("express");
const router = express.Router();
const { getVideoNames, getVideo , getArchieveNames, getArchieveVideo, addToArchieve, removeFromArchieve} = require("./videoApi");
const { userAuth } = require("../middleware/auth.js");

router.route("/getVideoNames").get(userAuth, getVideoNames);
router.route("/getVideo").get(userAuth, getVideo);
router.route("/getArchieveNames").get(userAuth, getArchieveNames);
router.route("/getArchieveVideo").get(userAuth, getArchieveVideo);
router.route("/addToArchieve").post(userAuth, addToArchieve);
router.route("/removeFromArchieve").post(userAuth, removeFromArchieve);

module.exports = router;
