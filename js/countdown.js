/*
Countdown timer for Survive Sac
Date: 9/24/2011 
Version: 1
redhedinsanityyyyyyy
*/

function countdown(outDiv,dDiv,hDiv,mDiv,sDiv) {

    var endDate = new Date(2012,05,26,19,00,00);
    var nowDate = new Date();
    var timeLeft = Math.floor((endDate.getTime()-nowDate.getTime())/1000); // time left in seconds before endDate
    
    if (timeLeft <= 0) { // if endDate is now or past
        document.getElementById(outDiv).innerHTML = "OUTBREAK";
    }
    else {
        var days = Math.floor(timeLeft/84600);
        timeLeft = timeLeft % 84600;
        var hrs = Math.floor(timeLeft/3600);
        timeLeft = timeLeft % 3600;
        var mins = Math.floor(timeLeft/60);
        timeLeft = timeLeft % 60;
        var secs = Math.floor(timeLeft);
    
        if (days < 10) {days = "0" + days;}
        if (hrs < 10) {hrs = "0" + hrs;}
        if (mins < 10) {mins = "0" + mins;}
        if (secs < 10) {secs = "0" + secs;}
        
        document.getElementById(dDiv).innerHTML = days;
        document.getElementById(hDiv).innerHTML = hrs;
        document.getElementById(mDiv).innerHTML = mins;
        document.getElementById(sDiv).innerHTML = secs;
        
        setTimeout(function(){countdown(outDiv,dDiv,hDiv,mDiv,sDiv);}, 1000);
    }
}
