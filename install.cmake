if(UNIX)
    SET(CMAKE_INSTALL_PREFIX /usr)


    # backend install in /usr/share/smithproxy/infra/bend/
    install(DIRECTORY src/infra/bend DESTINATION share/smithproxy/infra)
    # install infra/
    file(GLOB infra_py "src/infra/*.py" EXCLUDE "src/infra/smithdog.py")
    install(FILES ${infra_py} DESTINATION share/smithproxy/infra)

    file(GLOB infra_exe_py "src/infra/smithdog.py")
    install(FILES ${infra_exe_py} DESTINATION bin
            PERMISSIONS
            OWNER_READ OWNER_WRITE OWNER_EXECUTE
            GROUP_READ GROUP_EXECUTE
            WORLD_READ WORLD_EXECUTE
            RENAME sx_ctl
            )

    install(DIRECTORY src/infra/authtools DESTINATION share/smithproxy/infra)

    file(GLOB sx_auth_tools "src/infra/authtools/sx_*.py")
    install(FILES ${sx_auth_tools} DESTINATION share/smithproxy/infra/authtools
            PERMISSIONS
            OWNER_READ OWNER_WRITE OWNER_EXECUTE
            GROUP_READ GROUP_EXECUTE
            WORLD_READ WORLD_EXECUTE
            )

    install(FILES src/infra/authtools/sx_passwd.py  DESTINATION bin
            PERMISSIONS
            OWNER_READ OWNER_WRITE OWNER_EXECUTE
            GROUP_READ GROUP_EXECUTE
            WORLD_READ WORLD_EXECUTE
            RENAME sx_passwd
            )

    file(GLOB sx_www_cgi "src/infra/portal/cgi-bin/auth*.py")
    install(FILES ${sx_www_cgi} DESTINATION share/smithproxy/www/portal/cgi-bin
            PERMISSIONS
            OWNER_READ OWNER_WRITE OWNER_EXECUTE
            GROUP_READ GROUP_EXECUTE
            WORLD_READ WORLD_EXECUTE
            )
    file(GLOB sx_www_cgi_nox "src/infra/portal/cgi-bin/util.py")
    install(FILES ${sx_www_cgi_nox} DESTINATION share/smithproxy/www/portal/cgi-bin)

    file(GLOB sx_www "src/infra/portal/*.*")
    # install(DIRECTORY infra/portal DESTINATION share/smithproxy/www)
    install(FILES ${sx_www} DESTINATION share/smithproxy/www/portal/)



    # message: edit defaults and add to init.d to start at boot!
    install(CODE "MESSAGE(\" +----------------------------------------------------------------------------------------+\")")
    install(CODE "MESSAGE(\" | Auth component installation complete!                                                  |\")")
    install(CODE "MESSAGE(\" +----------------------------------------------------------------------------------------|\")")
    install(CODE "MESSAGE(\" |                                                                                        |\")")
    install(CODE "MESSAGE(\" +----------------------------------------------------------------------------------------+\")")

endif()
