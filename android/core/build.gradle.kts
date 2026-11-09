plugins {
    `java-library`
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
}

dependencies {
    api(libs.gson)
    testImplementation(libs.junit)
}

tasks.test {
    useJUnit()
    val projectRoot = rootProject.projectDir
    val repositoryRoot = if (projectRoot.name == "android") projectRoot.parentFile else projectRoot.parentFile.parentFile
    systemProperty("psicoia.repoRoot", repositoryRoot.absolutePath)
}
