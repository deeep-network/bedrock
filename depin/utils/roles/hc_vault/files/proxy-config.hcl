pid_file                = "/tmp/pidfile"
exit_after_auth         = true

vault {
  address               = "https://deeep-dev-public-vault-5a08f9b2.e0a0f93a.z1.hashicorp.cloud:8200"
  namespace             = "admin/deeep-network"

  retry {
    num_retries         = 5
  }
}

auto_auth {
   method {
    type                = "approle"
    namespace           = "admin/deeep-network"
    exit_on_err         = true

    config  = {
      role_id_file_path     = "/tmp/roleid"
      secret_id_file_path   = "/tmp/secretid"
      remove_secret_id_file_after_reading = true
      secret_id_response_wrapping_path = ""
    }
  }

  sink {
    type                = "file"
    wrap_ttl            = "30m"
    
    config  = {
      path              = "/tmp/sink.txt"
    }
  }
}

cache {
  // An empty cache stanza still enables caching
}

api_proxy {
  use_auto_auth_token   = true
}

listener "tcp" {
  address               = "127.0.0.1:8100"
  tls_disable           = true
}
