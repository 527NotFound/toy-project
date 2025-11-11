require "test_helper"

class ImageProcessesControllerTest < ActionDispatch::IntegrationTest
  test "should get new" do
    get image_processes_new_url
    assert_response :success
  end

  test "should get create" do
    get image_processes_create_url
    assert_response :success
  end

  test "should get show" do
    get image_processes_show_url
    assert_response :success
  end
end
