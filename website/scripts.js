const GET_URI_BUILDER_ENDPOINT = configs.APIGatewayUrl;
const identityPool = configs.identityPool;
const region = configs.region;

// Initialize the Amazon Cognito credentials provider
AWS.config.region = region; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: identityPool,
});

document.getElementById("launchButton").onclick = function(){

	document.getElementById('messageToUser').innerHTML = "";
	var username = $('#username').val();

	AWS.config.credentials.get(function(err) {
		if (err) alert(err);
	    
	    var awsCred = AWS.config.credentials;
	    var awsCredentials = {
		    region: region,
		    accessKeyId: awsCred.accessKeyId,
		    secretAccessKey: awsCred.secretAccessKey,
		    token: awsCred.sessionToken,
		};

		$.ajax(Signer(awsCredentials, {
		  url: GET_URI_BUILDER_ENDPOINT + '/build-uri',
		  type: 'POST',
		  dataType: 'json',
		  contentType: 'application/json',
		  data: { username: username },
		  success: function(response) {
		    //This call is performing search on text
			if ("errorMessage" in response){
				//alert("error from API");
    			document.getElementById('messageToUser').innerHTML = response['errorMessage'];
			} else if("directoryID" in response && 
			    response.directories.length == 1){	
			    // Redirect to the WorkSpaces URI
    			document.getElementById('messageToUser').innerHTML = 'Opening WorkSpace client for user '+username;
				window.location.href = response['directories'][0]['uri'];	
			} else if ( response.directories.length > 1) {
			    alert("Multiple Directories Found! Pick one.");
			}
			
		  }
		}));
	});

}
