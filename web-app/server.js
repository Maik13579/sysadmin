const express = require('express');
const https = require('https');
const bcrypt = require('bcrypt');
const path = require("path");
const bodyParser = require('body-parser');
const userDataManager = require('./userDataManager');
const fs = require('fs');

var options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};

const app = express();
const server = https.createServer(options, app);


app.use(express.json());
app.use("/auth", require("./Auth/route"))

/*
app.use(bodyParser.urlencoded({extended: false}));
app.use(express.static(path.join(__dirname,'./public')));


app.get('/', (req,res) => {
    res.sendFile(path.join(__dirname,'./public/index.html'));
});

app.post('/login', async (req, res) => {
    try{
        let users = userDataManager.loadUsers();
        let foundUser = users[0];
        const emailMatch = await bcrypt.compare(req.body.email, users[0].email);
        //.find((data) => bcrypt.compare(req.body.email, data.email));
        if (emailMatch) {
            let submittedPass = req.body.password;
            let storedPass = foundUser.password;

            const passwordMatch = await bcrypt.compare(submittedPass, storedPass);
            if (passwordMatch) {
                res.send(`<div align ='center'><h2>login successful</h2></div><br><br><br><div align ='center'><h3>Hello</h3></div><br><br><div align='center'><a href='./login.html'>logout</a></div>`);
            } else {
                res.send("<div align ='center'><h2>Invalid email or password</h2></div><br><br><div align ='center'><a href='./login.html'>login again</a></div>");
            }
        }
        else {

            let fakePass = `$2b$$10$ifgfgfgfgfgfgfggfgfgfggggfgfgfga`;
            await bcrypt.compare(req.body.password, fakePass);

            res.send("<div align ='center'><h2>Invalid email or password</h2></div><br><br><div align='center'><a href='./login.html'>login again<a><div>");
        }
    } catch(e) {
        res.send("Internal server error " + e);
    }
});
*/

server.listen(5000, () =>
    console.log("server is listening on port: 443")
)
process.on("unhandledRejection", err => {
  console.log(`An error occured: ${err.message}`);
  server.close(() => process.exit(1))
});
