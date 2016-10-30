var express = require('express');
var router = express.Router();
var logged = false;
/* GET home page. */
router.get('/', function (req, res, next) {
    if (!logged) {
        res.render('index', {
            title: 'OmniCam'
        })
    } else {
        res.redirect('/cameras')
    }
});
router.post('/login', function (req, res, next) {
    if (req.body.user == 'admin' && req.body.password == 'password') {
        logged = true
        res.redirect('/cameras')
    } else {
        res.redirect('/')
    }
});

router.get('/cameras', function (req, res, next) {
    res.render('camerapage', {
        title: 'Welcome Admin! - OmniCam'
    });
});

module.exports = router;