Use CloudFormation to deploy.

<td>
  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=WorkSpacesUserPortal&amp;templateURL=https://raw.githubusercontent.com/sdebrosse/amazonworkspaces_userportal/master/cloudformation.yaml" target="_blank">
   <span class="inlinemediaobject">
   <img src="images/cloudformation-launch-stack-button.png">
   </span>
  </a>
</td>


The website is hosted in an Amazon S3 bucket. The backend uses API Gateway, Lambda and Cognito (for authentication).
