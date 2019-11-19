var score='0';

function rating1(num) {
var name=['star1', 'star2', 'star3', 'star4', 'star5'];
var star=[document.getElementById(name[0].concat(num)), document.getElementById(name[1].concat(num)), 
document.getElementById(name[2].concat(num)), document.getElementById(name[3].concat(num)), document.getElementById(name[4].concat(num))];
var rate='rate';
var rating=document.getElementById(rate.concat(num));

    if(star[0].src.match("/static/main/star_full.png")){
        if(star[1].src.match("/static/main/star_full.png")){
            for(var i=1; i<5; i++){
                star[i].src="/static/main/star_empty.png";
                star[i].width="20";
                star[i].height="20";
                score='1';
            }
        }
        else{
            star[0].src="/static/main/star_empty.png";
            star[0].width="20";
            star[0].height="20";
            score='0';
        }
    }
    else
    {
        star[0].src="/static/main/star_full.png";
        star[0].width="20";
        star[0].height="20";
        score='1';
    }
    rating.value=score;
}

function rating2(num) {
var name=['star1', 'star2', 'star3', 'star4', 'star5'];
var star=[document.getElementById(name[0].concat(num)), document.getElementById(name[1].concat(num)), 
document.getElementById(name[2].concat(num)), document.getElementById(name[3].concat(num)), document.getElementById(name[4].concat(num))];
var rate='rate';
var rating=document.getElementById(rate.concat(num));
 
    if(star[1].src.match("/static/main/star_full.png")){
        if(star[2].src.match("/static/main/star_full.png")){
            for(var i=2; i<5; i++){
                star[i].src="/static/main/star_empty.png";
                star[i].width="20";
                star[i].height="20";
                  }
        }
        else{
            for(var i=0; i<2; i++){
              score='2';
            star[i].src="/main/star_empty.png";
                star[i].width="20";
                star[i].height="20";
                score='0';
            }
        }
    }
    else{
        for(var i=0; i<2; i++){
            star[i].src="/static/main/star_full.png";
            star[i].width="20";
            star[i].height="20";
            score='2';
        }
    }
    rating.value=score;
}

function rating3(num) {
var name=['star1', 'star2', 'star3', 'star4', 'star5'];
var star=[document.getElementById(name[0].concat(num)), document.getElementById(name[1].concat(num)), 
document.getElementById(name[2].concat(num)), document.getElementById(name[3].concat(num)), document.getElementById(name[4].concat(num))];
var rate='rate';
var rating=document.getElementById(rate.concat(num));

    if(star[2].src.match("/static/main/star_full.png")){
        if(star[3].src.match("/static/main/star_full.png")){
            for(var i=3; i<5; i++){
                star[i].src="/static/main/star_empty.png";
                star[i].width="20";
                star[i].height="20";
                score='3';
            }
        }
        else{
            for(var i=0; i<3; i++){
                star[i].src="/static/main/star_empty.png";
                star[i].width="20";
                star[i].height="20";
                score='0';
            }
        }
    }
    else{
        for(var i=0; i<3; i++){
            star[i].src="/static/main/star_full.png";
            star[i].width="20";
            star[i].height="20";
            score='3';
            }
    }
    rating.value=score;
}

function rating4(num) {
var name=['star1', 'star2', 'star3', 'star4', 'star5'];
var star=[document.getElementById(name[0].concat(num)), document.getElementById(name[1].concat(num)), 
document.getElementById(name[2].concat(num)), document.getElementById(name[3].concat(num)), document.getElementById(name[4].concat(num))];
var rate='rate';
var rating=document.getElementById(rate.concat(num));
 
    if(star[3].src.match("/static/main/star_full.png")){
        if(star[4].src.match("/static/main/star_full.png")){
            star[4].src="/static/main/star_empty.png";
            star[4].width="20";
            star[4].height="20";
            score='4';
        }
        else{
            for(var i=0; i<4; i++){
                star[i].src="/static/main/star_empty.png";
                star[i].width="20";
                star[i].height="20";
                score='0';
            }
        }
    }
    else{
        for(var i=0; i<4; i++){
            star[i].src="/static/main/star_full.png";
            star[i].width="20";
            star[i].height="20";
            score='4';
            }
    }
    rating.value=score;
}

function rating5(num) {
var name=['star1', 'star2', 'star3', 'star4', 'star5'];
var star=[document.getElementById(name[0].concat(num)), document.getElementById(name[1].concat(num)), 
document.getElementById(name[2].concat(num)), document.getElementById(name[3].concat(num)), document.getElementById(name[4].concat(num))];
var rate='rate';
var rating=document.getElementById(rate.concat(num));
 
    if(star[4].src.match("/static/main/star_full.png")){
        for(var i=0; i<5; i++){
            star[i].src="/static/main/star_empty.png";
            star[i].width="20";
            star[i].height="20";
            score='0';
        }
    }
    else{
        for(var i=0; i<5; i++){
            star[i].src="/static/main/star_full.png";
            star[i].width="20";
            star[i].height="20";
            score='5';
        }
    }
    rating.value=score;
}