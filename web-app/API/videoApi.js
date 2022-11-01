const path = require("path");
const validator = require('validator');
var fernet = require('fernet');
var fs = require('fs');

function validateInput(input) {
  if(validator.contains(input, '>') || validator.contains(input, '<') ||
  validator.contains(input, '&') || validator.contains(input, '\'') || validator.contains(input, '\"') || validator.contains(input, '/')) {
    return false;
  }

  return true;
}

symmetric_key = "zCm3lRnleW3gwiIJfRJGLPTHCrLN08bnkttZG4Wly6c=";

var token = new fernet.Token({
  secret: symmetric_key
});

directory = "../../videos/storage";
archieveDir = "../../videos/archieve";

exports.getVideoNames = async (req, res, next) => {
  var files = fs.readdirSync(path.join(__dirname, directory));
  if (files.length == 0) {
    return res.status(200).json({ message: "No files found" });
  }

  res.status(200).json(files);
};

exports.getVideo = async (req, res, next) => {
  let videoName = req.body.videoName;
  if (videoName === undefined) {
      console.log("GetVideo Request: No Video specified");
      return res.status(400).json({message: "No Video specified"});
  }

  // sanitize
  videoName = validator.trim(videoName);
  if (!validateInput(videoName)) {
    console.log("GetVideo Request: Video contains forbidden characters.");
    return res.status(400).json({message: "Request Denied: ", error: "Video name contains forbidden characters: < > & \' \" or /"});
  }

  
};
