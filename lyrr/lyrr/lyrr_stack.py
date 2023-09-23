from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as _api
)
from constructs import Construct

class LyrrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        # define the lambda functions
        docker_folder = "../lyrr/src"
        file_name = "lambda"            
        # lambda Function from docker image
        lambda_ = _lambda.DockerImageFunction(
            self, file_name,
            code=_lambda.DockerImageCode.from_image_asset(docker_folder, cmd=["lambda.handler"]),
        )
        
        # define the api
        api = _api.LambdaRestApi(
            scope=self,
            id="lyrr-api",
            handler=lambda_,
            proxy=True
        )

        lyrics = api.root.add_resource('lyrics')
        lyrics.add_method('GET')

        artists = api.root.add_resource('artists')
        artists.add_method('GET')

        train = api.root.add_resource('train')
        train.add_method('PUT')
        
