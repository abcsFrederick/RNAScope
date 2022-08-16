add_standard_plugin_tests(PACKAGE "girder_rnascope")

# add_python_test(rnascope PLUGIN RNAScope)

# add_web_client_test(
#     RNAScope
#     "${CMAKE_CURRENT_LIST_DIR}/plugin_tests/rnascopeSpec.js"
#     PLUGIN RNAScope
# )

# add_web_client_test(
#     imageViewer
#     "${CMAKE_CURRENT_LIST_DIR}/plugin_tests/imageViewerSpec.js"
#     PLUGIN RNAScope
#     TEST_MODULE "plugin_tests.rnascope_web_client_test"
#     TEST_PYTHONPATH "${CMAKE_CURRENT_LIST_DIR}:${PROJECT_SOURCE_DIR}/plugins/HistomicsTK/plugin_tests"
# )
# #set_property(TEST web_client_RNAScope.imageViewer APPEND PROPERTY ENVIRONMENT "TEST_FILES=${PROJECT_SOURCE_DIR}/plugins/large_image/plugin_tests/test_files")
# set_property(TEST web_client_RNAScope.imageViewer APPEND PROPERTY ENVIRONMENT "TEST_FILES=${PROJECT_SOURCE_DIR}/plugins/RNAScope/plugin_tests")
