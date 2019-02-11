Use CloudFormation to deploy.

<td>
  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=WorkSpacesUserPortal&amp;templateURL=https://s3-us-west-2.amazonaws.com/debrosse-cloudformation-templates/cloudformation.yaml" target="_blank">
   <span class="inlinemediaobject">
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png">
   </span>
  </a>
</td>

<br>
The website is hosted in an Amazon S3 bucket. The backend uses API Gateway, Lambda and Cognito (for authentication). A WorkSpaces URI string is built and returned to the user's browser. The WorkSpaces client is automatically launched and the Registration Code and username is automatically filled in.
<br>
<img src="architecture.png">

<br>
Clean up: Remove all objects from your S3 bucket. Then delete the CloudFormation stack and all resources will be cleaned up.
