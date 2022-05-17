const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require("path");
const cookieParser = require("cookie-parser");
const { adminAuth, userAuth } = require("./middleware/auth.js");
const helmet = require("helmet");

var options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};
'use strict'
const app = express();
app.use(
  helmet({
    contentSecurityPolicy: false,
  })
);

const server = https.createServer(options, app);


app.use(express.json());
app.use(cookieParser());
app.use("/auth", require("./Auth/route"));

app.get('/', (req,res) => {
    res.sendFile(path.join(__dirname,'./public/index.html'));
});

app.get('/admin/register', adminAuth, (req,res) => {
    res.sendFile(path.join(__dirname,'./public/register.html'));
});

app.get('/login', (req,res) => {
    res.sendFile(path.join(__dirname,'./public/login.html'));
});

app.get('/admin', adminAuth, (req,res) => {
    res.sendFile(path.join(__dirname,'./public/admin.html'));
});

app.get('/home', userAuth, (req,res) => {
    res.sendFile(path.join(__dirname,'./public/home.html'));
});

app.get('/logout', (req,res) => {
    res.cookie("jwt", "", { maxAge: "1" });
    res.redirect("/");
});

server.listen(443, () =>
    console.log("server is listening on port: 443")
)
process.on("unhandledRejection", err => {
  console.log(`An error occured: ${err.message}`);
  server.close(() => process.exit(1))
});
