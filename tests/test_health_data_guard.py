import pytest
from health_data_guard import build_docker_image, deploy_to_kubernetes, Policy

def test_build_docker_image():
    version = "1.0.0"
    expected_image = "health-data-guard:1.0.0"
    assert build_docker_image(version) == expected_image

def test_deploy_to_kubernetes():
    policy_store_url = "https://example.com/policy-store"
    image = "health-data-guard:1.0.0"
    expected_output = f"Deployed {image} to Kubernetes with policy store URL: {policy_store_url}"
    assert deploy_to_kubernetes(policy_store_url, image) == expected_output

def test_main():
    # Test with valid arguments
    with pytest.raises(SystemExit) as exit_info:
        import sys
        sys.argv = ["health_data_guard.py", "--version", "1.0.0", "--policy-store-url", "https://example.com/policy-store"]
        from health_data_guard import main
        main()
    assert exit_info.value.code == 0

    # Test with missing arguments
    with pytest.raises(SystemExit) as exit_info:
        import sys
        sys.argv = ["health_data_guard.py"]
        from health_data_guard import main
        main()
    assert exit_info.value.code == 2
