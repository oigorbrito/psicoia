pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "PsicoIAAndroid"
include(":app", ":core", ":llama")
project(":llama").projectDir = file("third_party/llama.cpp/examples/llama.android/lib")
