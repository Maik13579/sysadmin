const rateLimit = require("express-rate-limit");

const limiter = rateLimit({
  windowMs: 5 * 1000, // 5s
  max: 2 // each IP can do max requests in windowMs timeframe
});

module.exports = limiter;
