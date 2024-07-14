let verify = window.sessionStorage.getItem('Verifier');
let state = window.sessionStorage.getItem('State');
const sha256 = async (plain) => {
    const encoder = new TextEncoder()
    const data = encoder.encode(plain)
    return window.crypto.subtle.digest('SHA-256', data)
  }
  

const base64encode = (input) => {
    return btoa(String.fromCharCode(...new Uint8Array(input)))
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_');
  }
let challenge = window.sessionStorage.getItem('Challenge');
console.log(challenge)
console.log(verify)

let code = new URLSearchParams(window.location.search).get('code');
let stateFromUrl = new URLSearchParams(window.location.search).get('state');
function getLocation(){
    if (navigator.geolocation){
        navigator.geolocation.getCurrentPosition(showPosition);
        document.getElementById("errorDisplay").textContent = "Geolocation is done!";
    } 
    else{
        document.getElementById("errorDisplay").textContent = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position){
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
    window.localStorage.setItem('latitude', latitude);
    window.localStorage.setItem('longitude', longitude);
}

getLocation();
let latitude = window.localStorage.getItem('latitude');
let longitude = window.localStorage.getItem('longitude');
if (stateFromUrl === state) {
    console.log("State parameter matches the expected value.");
    // Proceed with your logic
    fetch("/api/token", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body : JSON.stringify({grant_type : "authorization_code", code : code, redirect_uri : "https://www.musicalmiles.co/callback.html" , code_verifier : verify , latitude : latitude, longitude : longitude})
        
        }).then(function(response) {
            if (response.status === 200) {
                response.json().then(function(r) {
                    console.log(r);
                    u = r.user; // Changed from r.User to r.user to match the returned object
                    window.sessionStorage.setItem("musicalMilesID", r.id)
                    if (u==="New"){
                        window.location.href = "newUser.html";
                    }
                    else if (u==="Existing"){
                        window.location.href = "oldUser.html";
                    }
                    
                });
            }
        });
} else {
    console.log("State parameter does not match the expected value.");
    // Handle the error, e.g., show an error message or redirect
    document.getElementById("errorDisplay").textContent = "Please  Refresh and allow location.";
}

