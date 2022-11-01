const path = require("path");
const validator = require('validator');
const {spawn} = require("child_process");
var fs = require('fs');

function validateInput(input) {
  if(validator.contains(input, '>') || validator.contains(input, '<') ||
  validator.contains(input, '&') || validator.contains(input, '\'') || validator.contains(input, '\"') || validator.contains(input, '/')) {
    return false;
  }

  return true;
}

symmetric_key = "zCm3lRnleW3gwiIJfRJGLPTHCrLN08bnkttZG4Wly6c=";

directory = "../../videos/storage";
tempDir = "../../videos/temp";
archieveDir = "../../videos/archieve";

exports.getVideoNames = async (req, res, next) => {
  var files = fs.readdirSync(path.join(__dirname, directory));
  if (files.length == 0) {
    return res.status(200).json({ message: "No files found" });
  }

  res.status(200).json(files);
};

exports.getVideo = async (req, res, next) => {
  let videoName = req.query.videoName;
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

  const filePath = path.join(path.join(__dirname, directory), videoName);
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ message: "Video not found"});
  }

  var dataToSend;
  const python = spawn('python', ['API/decryptVideo.py', videoName]);
  python.stdout.on('data', function(data) {
    dataToSend = data.toString();
  });

  python.stderr.on('data', data => {
    console.log(data.toString());
  });

  python.on('exit', (code) => {
    if (code == 0) {
      console.log("Decrypted file");
      let tempFilePath = path.join(path.join(__dirname, tempDir), videoName);
      res.status(200).download(tempFilePath, err => {
        fs.unlink(tempFilePath, err => {});
      });
    }
  });
};
