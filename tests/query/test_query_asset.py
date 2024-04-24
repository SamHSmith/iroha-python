import allure
import pytest

from tests import client

@pytest.fixture(scope="function", autouse=True)
def story_account_queries_assets():
    allure.dynamic.story("Account queries assets")
    allure.dynamic.label("permission", "no_permission_required")

@allure.label("sdk_test_id", "query_all_assets_owned_by_account")
def test_query_all_assets_owned_by_account(
        GIVEN_registered_account_with_minted_assets):
    with allure.step(
            f'WHEN client queries all assets owned by account "{GIVEN_registered_account_with_minted_assets}"'):
        assets_owned_by_account = client.query_all_assets_owned_by_account(GIVEN_registered_account_with_minted_assets)
    with allure.step(
            f'THEN the response should be a non-empty list of assets owned by account "{GIVEN_registered_account_with_minted_assets}"'):
        assert isinstance(assets_owned_by_account, list) and assets_owned_by_account, \
            f"Expected a non-empty list of assets owned by account {GIVEN_registered_account_with_minted_assets}, got {assets_owned_by_account}"

@allure.label("sdk_test_id", "query_all_assets")
def test_query_all_assets():
    with allure.step('WHEN client queries all assets'):
        all_assets = client.query_all_assets()
    with allure.step('THEN the response should be a non-empty list of assets'):
        assert isinstance(all_assets, list) and all_assets, \
            f"Expected a non-empty list of assets, got {all_assets}"

@allure.label("sdk_test_id", "query_all_asset_definitions")
def test_query_all_asset_definitions():
    with allure.step('WHEN client queries all asset definitions'):
        all_asset_definitions = client.query_all_asset_definitions()
    with allure.step('THEN the response should be a non-empty list of asset definitions'):
        assert isinstance(all_asset_definitions, list) and all_asset_definitions, \
            f"Expected a non-empty list of asset definitions, got {all_asset_definitions}"


    