from constructs import Construct
from aws_cdk import (
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    RemovalPolicy,
)
from pathlib import Path
import subprocess
import sys


class FrontendStack(Construct):
    """
    CDK Construct for deploying React frontend to S3 + CloudFront.
    
    This construct creates:
    - S3 bucket for static website hosting
    - CloudFront Origin Access Identity (OAI) for secure S3 access
    - CloudFront distribution with custom error responses for SPA routing
    - CfnOutputs for deployment automation
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_name: str,
        region: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.stack_name = stack_name
        self.region = region
        
        # Create S3 bucket for static website hosting
        self._create_s3_bucket()
        
        # Create CloudFront Origin Access Identity
        self._create_origin_access_identity()
        
        # Create CloudFront distribution
        self._create_cloudfront_distribution()
        
        # Deploy frontend assets (if dist directory exists)
        self._deploy_frontend_assets()
        
        # Create outputs
        self._create_outputs()
    
    def _create_s3_bucket(self) -> None:
        """
        Create S3 bucket for CloudFront origin.
        
        Note: We do NOT enable S3 website hosting because we're using CloudFront
        with Origin Access Identity (OAI). Website hosting is incompatible with OAI.
        CloudFront will handle the SPA routing via error responses.
        """
        self.frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=f"{self.stack_name}-frontend-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # CloudFront will access via OAI
        )
    
    def _create_origin_access_identity(self) -> None:
        """Create CloudFront Origin Access Identity for secure S3 access."""
        self.origin_access_identity = cloudfront.OriginAccessIdentity(
            self,
            "FrontendOAI",
            comment=f"OAI for {self.stack_name} frontend bucket"
        )
        
        # Grant CloudFront OAI read access to S3 bucket
        self.frontend_bucket.grant_read(self.origin_access_identity)
    
    def _create_cloudfront_distribution(self) -> None:
        """Create CloudFront distribution with SPA routing support."""
        self.distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.frontend_bucket,
                    origin_access_identity=self.origin_access_identity
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                compress=True,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=None,
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=None,
                ),
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_200,
        )
    
    def _build_frontend(self) -> bool:
        """
        Build the frontend application.
        
        Returns:
            bool: True if build succeeded, False otherwise
        """
        frontend_path = Path(__file__).parent.parent.parent / "frontend"
        
        if not frontend_path.exists():
            print(f"Warning: Frontend directory not found at {frontend_path}")
            return False
        
        print("=" * 60)
        print("Building frontend application...")
        print("=" * 60)
        
        try:
            # Clean dist directory to force fresh build
            dist_path = frontend_path / "dist"
            if dist_path.exists():
                print("Cleaning previous build...")
                import shutil
                shutil.rmtree(dist_path)
                print("✓ Previous build cleaned")
            
            # Check if node_modules exists, if not run npm install
            node_modules_path = frontend_path / "node_modules"
            if not node_modules_path.exists():
                print("Installing npm dependencies...")
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=str(frontend_path),
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("✓ Dependencies installed")
            
            # Run npm build
            print("Running npm build...")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(frontend_path),
                capture_output=True,
                text=True,
                check=True
            )
            print("✓ Frontend build completed successfully")
            print("=" * 60)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Frontend build failed!")
            print(f"Error: {e.stderr}")
            print("=" * 60)
            return False
        except FileNotFoundError:
            print("✗ npm not found. Please install Node.js and npm.")
            print("=" * 60)
            return False
    
    def _deploy_frontend_assets(self) -> None:
        """
        Build and deploy frontend build artifacts to S3 bucket.
        
        This method automatically builds the frontend before deployment.
        """
        # Get path to frontend dist directory
        frontend_dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
        
        # Build the frontend
        build_success = self._build_frontend()
        
        if not build_success:
            print("Warning: Frontend build failed. Skipping deployment.")
            print("You can manually build with: cd frontend && npm run build")
            return
        
        # Verify dist directory exists after build
        if not frontend_dist_path.exists() or not frontend_dist_path.is_dir():
            print(f"Warning: Frontend dist directory not found at {frontend_dist_path}")
            print("Build may have failed. Check the output above.")
            return
        
        # Deploy to S3
        print("Deploying frontend to S3...")
        self.deployment = s3deploy.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[s3deploy.Source.asset(str(frontend_dist_path))],
            destination_bucket=self.frontend_bucket,
            distribution=self.distribution,
            distribution_paths=["/*"],  # Invalidate all CloudFront cache
            prune=True,  # Remove old files from bucket
            memory_limit=512,  # MB for deployment Lambda
        )
        print("✓ Frontend deployment configured")
    
    def _create_outputs(self) -> None:
        """Create CloudFormation outputs for deployment automation."""
        CfnOutput(
            self,
            "CloudFrontDomainName",
            value=self.distribution.distribution_domain_name,
            description="CloudFront distribution domain name",
            export_name=f"{self.stack_name}-CloudFrontDomainName"
        )
        
        CfnOutput(
            self,
            "CloudFrontDistributionURL",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="CloudFront distribution URL",
            export_name=f"{self.stack_name}-CloudFrontURL"
        )
        
        CfnOutput(
            self,
            "FrontendBucketName",
            value=self.frontend_bucket.bucket_name,
            description="S3 bucket name for frontend deployment",
            export_name=f"{self.stack_name}-FrontendBucketName"
        )
