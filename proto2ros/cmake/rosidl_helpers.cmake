# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

# Adds Python sources to an existing rosidl generated Python package.
#
# :param target: the target name for the file transfer, so it can be depended on.
# :param MODULES: Python modules (i.e. files) to be added. These will copied
#   under the rosidl generated Python package. No directory structure will
#   be kept.
# :param PACKAGES: Python packages (i.e. directories) to be added. Their content
#   will be copied under the rosidl generated Python Package. Their directory
#   structure will be kept.
# :param DESTINATION: the rosidl_generate_interfaces target that the destination
#   Python package is associated with. Defaults to the current project name.
function(rosidl_generated_python_package_add target)
  cmake_parse_arguments(ARG "" "DESTINATION" "MODULES;PACKAGES" ${ARGN})
  if(NOT ARG_DESTINATION)
    set(ARG_DESTINATION ${PROJECT_NAME})
  endif()
  if(NOT ARG_MODULES AND NOT ARG_PACKAGES)
    message(FATAL_ERROR "No modules nor packages to add")
  endif()
  set(OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_py/${ARG_DESTINATION}")

  if(ARG_MODULES)
    unset(input_files)
    unset(output_files)
    foreach(module ${ARG_MODULES})
      get_filename_component(module_name "${module}" NAME)
      list(APPEND output_files "${OUTPUT_DIR}/${module_name}")
      get_filename_component(module_path "${module}" ABSOLUTE)
      list(APPEND input_files "${module_path}")
    endforeach()
    add_custom_command(
      OUTPUT ${output_files}
      COMMAND ${CMAKE_COMMAND} -E copy ${input_files} ${OUTPUT_DIR}/.
      DEPENDS ${input_files}
    )
    list(APPEND OUTPUT_FILES ${output_files})
  endif()

  if(ARG_PACKAGES)
    unset(input_files)
    unset(output_files)
    foreach(package ${ARG_PACKAGES})
      get_filename_component(package_path "${package}" ABSOLUTE)
      file(GLOB_RECURSE package_files "${package_path}" *.py)
      foreach(input_file ${package_files})
        get_filename_component(module_name "${module}" NAME)
        file(RELATIVE_PATH output_file ${package_path} "${input_file}")
        list(APPEND output_files "${OUTPUT_DIR}/${output_file}")
      endforeach()
      list(APPEND input_dirs "${package_path}")
      list(APPEND input_files "${package_files}")
    endforeach()
    add_custom_command(
      OUTPUT ${output_files}
      COMMAND ${CMAKE_COMMAND} -E copy_directory ${input_dirs} ${OUTPUT_DIR}/.
      DEPENDS ${input_files} ${input_dirs}
    )
    list(APPEND OUTPUT_FILES ${output_files})
  endif()

  add_custom_target(${target} ALL DEPENDS ${OUTPUT_FILES})
  add_dependencies(${target} ${ARG_DESTINATION})
endfunction()

# Exports relevant variables to setup tests that depend on rosidl generated artifacts.
#
# :param LIBRARY_DIRS: the name of the variable to yield the paths
#   where generated shared library may be found.
# :param ENV: the name of the variable to yield relevant environment
#   variable values pointing to generated artifacts (such as PYTHONPATH).
function(get_rosidl_generated_interfaces_test_setup)
  cmake_parse_arguments(ARG "" "LIBRARY_DIRS;ENV" "" ${ARGN})
  if(ARG_LIBRARY_DIRS)
    set(${ARG_LIBRARY_DIRS} "${CMAKE_CURRENT_BINARY_DIR}" PARENT_SCOPE)
  endif()
  if(ARG_ENV)
    set(${ARG_ENV} "PYTHONPATH=${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_py" PARENT_SCOPE)
  endif()
endfunction()
