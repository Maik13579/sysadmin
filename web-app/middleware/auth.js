const jwt = require("jsonwebtoken");
const jwtSecret = '5ab67fbe236d1025a9b52b6179a8db6dca16a4d0a4a843c86c09535feb0ddaddc82f8b';

exports.adminAuth = (req, res, next) => {
  const token = req.cookies.jwt;

  if (token) {
    jwt.verify(token, jwtSecret, (err, decodedToken) => {
      if (err) {
        console.log("AdminAuth: " + err);
        return res.status(401).json({ message: "Not authorized" });
      }
      else {
        if (decodedToken.role !== "Admin") {
          console.log("AdminAuth: Not authorized");
          return res.status(401).json({ message: "Not authorized" });
        }
        else {
          console.log("AdminAuth: granted");
          next();
        }
      }
    });
  }
  else {
    return res.status(401).redirect("/home");
  }
};

exports.userAuth = (req, res, next) => {
  const token = req.cookies.jwt;

  if (token) {
    jwt.verify(token, jwtSecret, (err, decodedToken) => {
      if (err) {
        console.log("BasicAuth: " + err);
        return res.status(401).json({ message: "Not authorized" });
      }
      else {
        if (decodedToken.role !== "Basic" && decodedToken.role !== "Admin") {
          console.log("BasicAuth: Not authorized");
          return res.status(401).json({ message: "Not authorized" });
        }
        else {
          console.log("BasicAuth: granted");
          next();
        }
      }
    });
  }
  else {
    return res.status(401).redirect("/");
  }
};
