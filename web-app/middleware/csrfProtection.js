const csrf = require("csurf");

const csrfProtection = csrf({
  cookie: {
    secure: true,
    httpOnly: true,
    maxAge: 60 * 60,
  }
});

module.exports = csrfProtection;
