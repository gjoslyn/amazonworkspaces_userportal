var GET_URI_BUILDER_ENDPOINT = "API GATEWAY HTTPS ENDPOINT"

// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'us-west-2'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'COGNITO POOL ID',
});

document.getElementById("launchButton").onclick = function(){

	document.getElementById('messageToUser').innerHTML = "";
	var username = $('#username').val();

	AWS.config.credentials.get(function(err) {
		if (err) alert(err);
	    
	    var awsCred = AWS.config.credentials;
	    var awsCredentials = {
		    region: 'us-west-2',
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
			}
			
			if("uri" in response){
				// Redirect to the WorkSpaces URI
    			document.getElementById('messageToUser').innerHTML = 'Opening WorkSpace client for user '+username;
				window.location.href = response['uri'];	
			}
		  }
		}));
	});

}
