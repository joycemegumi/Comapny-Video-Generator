# Automating Content Creation with a Serverless Architecture
## Transforming a 2 Million+ Companies Dataset into Dynamic Video Presentations
### Authors: Joyce Megumi Ishikawa, Shuyan Wu, Myesha Sokhey, Jiayun Huang

[View the Web Application](https://frontendcodegroup2.s3.amazonaws.com/videogenerator.html)

[View Demo: Generating New Video](https://youtu.be/qe13jgi8Dv4)

[View Demo: Generating Existing Video](https://youtu.be/1GhVirfRe0Q)

[View the Canva Presenation](https://www.canva.com/design/DAFr0hoDX14/3IRODlYJekxRvXHBT6kVJA/view?utm_content=DAFr0hoDX14&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink)

Manual content creation involves extensive time and effort by video editors that need to search for video assets, apply copy, styling etc. This process can be time-consuming and may lead to delays in delivering timely content to customers, potentially missing valuable opportunities.

In this project my team built a company video generator web application based on companies datasets from Kaggle. This cutting-edge platform will allow users to effortlessly generate videos by simply selecting their company name and desired theme by leveraging the integration of the [JSON2Video API](https://json2video.com/) and [Pexel API](https://www.pexels.com/api/).

Benefits :
* Cost and time efficiency in content creation.
* Enabling non-technical users to create videos.

<img src="Company Video Generation Cloud Architecture.jpeg"/>

Please be aware that if the site experiences downtime or malfunctions, it could be due to the following reasons:
* AWS Lab Budget Depletion: The site relies on AWS lab resources. Budget constraints might lead to temporary unavailability.
* JSON2VIDEO API Key Trial End: Some features use the JSON2VIDEO API with a free trial. If the trial ends, related services might be affected.
