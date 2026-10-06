plugins {
    id("java")
    kotlin("jvm") version "1.9.25"
    id("org.jetbrains.intellij.platform") version "2.1.0"
}

group = "com.pycn"
version = "0.1.0"

repositories {
    mavenCentral()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    intellijPlatform {
        // 基于 IntelliJ IDEA Community 2024.2 构建；PyCharm Community 亦可
        intellijIdeaCommunity("2024.2")
        instrumentationTools()
    }
}

intellijPlatform {
    pluginConfiguration {
        name = "PyCn 中文编程语言"
        version = "0.1.0"
        ideaVersion {
            sinceBuild = "242"
            untilBuild = "251.*"
        }
    }
}

kotlin {
    jvmToolchain(17)
}

tasks {
    withType<JavaCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }
}
