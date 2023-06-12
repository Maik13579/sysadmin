const path = require("path");
const validator = require('validator');
const {spawn} = require("child_process");
var fs = require('fs');

let timerDicc = new Object();

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
    return res.status(404).json({ message: "No files found" });
  }

  res.status(200).json(files);
};

exports.deleteVideoStream = async (req, res, next) => {
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

  const decryptedFilePath = path.join(path.join(__dirname, tempDir), videoName);
  if (fs.existsSync(decryptedFilePath)) {
    deleteTemp(decryptedFilePath);
    if (videoName in timerDicc) {
      clearTimeout(timerDicc[videoName]);
      delete timerDicc[videoName];
    }
  }

  res.status(200).json({message: "Video stram closed"});
};

exports.getVideo = async (req, res, next) => {
  let videoName = req.query.videoName;
  let isArchieved = req.query.archieved;
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

  const decryptedFilePath = path.join(path.join(__dirname, tempDir), videoName);
  if (fs.existsSync(decryptedFilePath)) {
    streamVideo(req, res, videoName);
    return;
  }

  let filePath = path.join(path.join(__dirname, directory), videoName);
  if (isArchieved === false) {
    filePath = path.join(path.join(__dirname, archieveDir), videoName);
  }

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
      streamVideo(req, res, videoName);
    }
  });
};

function streamVideo(req, res, videoName) {
  const range = req.headers.range;
  if (!range) {
      res.status(400).send("Requires Range header");
  }

  let tempFilePath = path.join(path.join(__dirname, tempDir), videoName);
  const videoSize = fs.statSync(tempFilePath).size;
  const CHUNK_SIZE = 10 ** 6;
  const start = Number(range.replace(/\D/g, ""));
  const end = Math.min(start + CHUNK_SIZE, videoSize - 1);
  const contentLength = end - start + 1;
  const headers = {
      "Content-Range": `bytes ${start}-${end}/${videoSize}`,
      "Accept-Ranges": "bytes",
      "Content-Length": contentLength,
      "Content-Type": "video/mp4",
  };
  res.writeHead(206, headers);
  const videoStream = fs.createReadStream(tempFilePath, { start, end });
  videoStream.pipe(res);

  if (videoName in timerDicc) {
    clearTimeout(timerDicc[videoName]);
    delete timerDicc[videoName];
  }

  timerDicc[videoName] = setTimeout(deleteTemp, 60000, tempFilePath);
}

function deleteTemp(tempFilePath) {
  fs.unlink(tempFilePath, err => {});
}

exports.getArchieveNames = async (req, res, next) => {
  var files = fs.readdirSync(path.join(__dirname, archieveDir));
  if (files.length == 0) {
    return res.status(404).json({ message: "No files found" });
  }

  res.status(200).json(files);
};

exports.getArchieveVideo = async (req, res, next) => {
  let videoName = req.query.videoName;
  if (videoName === undefined) {
      console.log("getArchieveVideo Request: No Archieve Video specified");
      return res.status(400).json({message: "No Archieve Video specified"});
  }

  // sanitize
  videoName = validator.trim(videoName);
  if (!validateInput(videoName)) {
    console.log("getArchieveVideo Request: Archieve Video contains forbidden characters.");
    return res.status(400).json({message: "Request Denied: ", error: "Archieve Video name contains forbidden characters: < > & \' \" or /"});
  }

  const filePath = path.join(path.join(__dirname, archieveDir), videoName);
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ message: "Archieve Video not found"});
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
    else {
      res.status(400).json({message: "Something went wrong while decrypting your Video"})
    }
  });
};

exports.addToArchieve = async (req, res, next) => {
  let videoName = req.query.videoName;
  if (videoName === undefined) {
      console.log("addToArchieve Request: No Video to archieve specified");
      return res.status(400).json({message: "No Video to archieve specified"});
  }

  // sanitize
  videoName = validator.trim(videoName);
  if (!validateInput(videoName)) {
    console.log("addToArchieve Request: Video to archieve contains forbidden characters.");
    return res.status(400).json({message: "Request Denied: ", error: "Video to archieve name contains forbidden characters: < > & \' \" or /"});
  }

  const filePath = path.join(path.join(__dirname, directory), videoName);
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ message: "Video to archieve not found"});
  }

  let targetPath = path.join(path.join(__dirname, archieveDir), videoName);
  fs.rename(filePath, targetPath, function (err) {
    if (err) {
        return res.status(400).json({message: "Request Denied: ", error: err});
    }
  });

  res.status(200).json({message: "Added Video to Archieve"});
};

exports.removeFromArchieve = async (req, res, next) => {
  let videoName = req.query.videoName;
  if (videoName === undefined) {
      console.log("removeFromArchieve Request: No Archieve Video specified");
      return res.status(400).json({message: "No Archieve Video specified"});
  }

  // sanitize
  videoName = validator.trim(videoName);
  if (!validateInput(videoName)) {
    console.log("removeFromArchieve Request: Archieve Video contains forbidden characters.");
    return res.status(400).json({message: "Request Denied: ", error: "Archieve Video name contains forbidden characters: < > & \' \" or /"});
  }

  const filePath = path.join(path.join(__dirname, archieveDir), videoName);
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ message: "Archieve Video not found"});
  }

  let targetPath = path.join(path.join(__dirname, directory), videoName);
  fs.rename(filePath, targetPath, function (err) {
    if (err) {
        return res.status(400).json({message: "Request Denied: ", error: err});
    }
    else {
      res.status(200).json({message: "Added Video to Archieve"});
    }
  });
};
