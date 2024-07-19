

# def test_filter_return_403_when_no_header_present(test_app_unauthorised):
# jwt = JWT(issued_at=int(datetime.now().timestamp()), token_id=uuid4(), algorith=JWT.SUPPORTED_ALGORITHM)
#     with test_app_unauthorised.test_request_context(
#             "/notes", method="GET", headers={'Authorization': 'Bearer XXXXX')}
#     ):