const express = require("express");
const router = express.Router();

const { generateDebate } = require("../services/debateService");

router.post("/", generateDebate);

module.exports = router;