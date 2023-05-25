const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require("path");
const cookieParser = require("cookie-parser");
const { adminAuth, userAuth } = require("./middleware/auth.js");
const helmet = require("helmet");
var bodyParser = require('body-parser');
const csrfProtection = require("./middleware/csrfProtection.js");

// https
var options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};

const app = express();

app.set("view engine", "ejs");

app.use(
  helmet({
    contentSecurityPolicy: false,
  })
);

const server = https.createServer(options, app);

app.use(express.json());
app.use(cookieParser());
app.use(csrfProtection);


// error handler
app.use(function (err, req, res, next) {
  if (err.code !== 'EBADCSRFTOKEN') {
    return next(err);
  }

  // handle CSRF token errors here
  console.log("CSRF Not Valid: " + req.headers);
  return res.status(403).json({message: "Request failed", error: "Request Origin not valid"});
});

app.use("/auth", require("./Auth/route"));
app.use("/videoApi", require("./API/route"));

app.get('/', (req,res) => {
    res.render('index');
});

app.get('/admin/register', adminAuth, (req,res) => {
    res.render('register', { csrfToken: req.csrfToken() });
});

app.get('/login', (req,res) => {
    res.render('login', { csrfToken: req.csrfToken() });
});

app.get('/admin', adminAuth, (req,res) => {
    res.render('admin', { csrfToken: req.csrfToken() });
});

app.get('/home', userAuth, (req,res) => {
    res.render('home', { csrfToken: req.csrfToken() });
});

app.get('/mediaPlayer', userAuth, (req,res) => {
    res.render('mediaPlayer', { csrfToken: req.csrfToken() });
});

app.get('/logout', (req,res) => {
    res.cookie("jwt", "", { maxAge: "1" });
    res.redirect("/");
});

server.listen(443, () =>
    console.log("server is listening on port: 443")
);
process.on("unhandledRejection", err => {
  console.log(`An error occured: ${err.message}`);
  server.close(() => process.exit(1));
});
