const generateRandomString = (length) => {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const values = crypto.getRandomValues(new Uint8Array(length));
    return values.reduce((acc, x) => acc + possible[x % possible.length], "");
  }

  async function sha256(plain) {
    const encoder = new TextEncoder()
    const data = encoder.encode(plain)
  
    return window.crypto.subtle.digest('SHA-256', data)
  }
  
  function base64urlencode(a){
    return btoa(String.fromCharCode.apply(null, new Uint8Array(a)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
}

          

        const encryption = async () => {
            let codeVerifier = generateRandomString(64);
            
            const hashed = await sha256(codeVerifier);
            const codeChallenge = base64urlencode(hashed);
            
            
            console.log(codeChallenge);


            const clientId = '18cd51e587a34060b5bfa3a32363441f';
            const redirectUri = 'https://www.musicalmiles.co/callback.html';
            const scope = 'user-read-private user-read-email user-read-recently-played user-read-currently-playing';
            const authUrl = new URL("https://accounts.spotify.com/authorize");

            // Store the code verifier in local storage
            window.sessionStorage.setItem('code_verifier', codeVerifier);
            let State = generateRandomString(64);
            const params = {
                response_type: 'code',
                client_id: clientId,
                state: State,
                scope : scope,
                code_challenge_method: 'S256',
                code_challenge: codeChallenge,
                redirect_uri: redirectUri
                
            };

            authUrl.search = new URLSearchParams(params).toString();
            window.location.href = authUrl.toString();
            window.sessionStorage.setItem('State', State);
            window.sessionStorage.setItem('Verifier', codeVerifier);
            window.sessionStorage.setItem('Challenge', codeChallenge);
       

console.log(state);
console.log(codeVerifier);
console.log(codeChallenge);
 }
