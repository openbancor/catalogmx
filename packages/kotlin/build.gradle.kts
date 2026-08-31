plugins {
    kotlin("jvm") version "1.9.22"
    kotlin("plugin.serialization") version "1.9.22"
    id("org.jetbrains.dokka") version "1.9.10"
    id("io.gitlab.arturbosch.detekt") version "1.23.4"
    id("com.vanniktech.maven.publish") version "0.34.0"
    jacoco
}

group = "com.openbancor"
version = "0.7.0"
description = "Mexican financial and government catalog data library for Kotlin/JVM"

repositories {
    mavenCentral()
}

dependencies {
    // Kotlin serialization for JSON parsing
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")

    // SQLite JDBC for database access
    implementation("org.xerial:sqlite-jdbc:3.44.1.0")

    // HTTP client for data updates
    implementation("io.ktor:ktor-client-core:2.3.7")
    implementation("io.ktor:ktor-client-cio:2.3.7")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")

    // ICU4J for Unicode/diacritics handling
    implementation("com.ibm.icu:icu4j:74.2")

    // Testing
    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("org.junit.jupiter:junit-jupiter-params:5.10.1")
    testImplementation("io.mockk:mockk:1.13.8")

    // Faker for test data generation
    testImplementation("io.github.serpro69:kotlin-faker:1.15.0")
}

kotlin {
    jvmToolchain {
        languageVersion.set(JavaLanguageVersion.of(System.getenv("JAVA_VERSION")?.toIntOrNull() ?: 17))
    }
}

tasks.test {
    useJUnitPlatform()
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}

tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = "0.85".toBigDecimal()
            }
        }
    }
}

detekt {
    buildUponDefaultConfig = true
    config.setFrom("$projectDir/detekt.yml")
}

mavenPublishing {
    coordinates("com.openbancor", "catalogmx", project.version.toString())
    publishToMavenCentral()

    pom {
        name.set("catalogmx")
        description.set(project.description)
        url.set("https://github.com/openbancor/catalogmx")

        licenses {
            license {
                name.set("BSD 2-Clause License")
                url.set("https://opensource.org/license/bsd-2-clause")
                distribution.set("repo")
            }
        }

        developers {
            developer {
                id.set("openbancor")
                name.set("OpenBancor")
                email.set("dev@openbancor.com")
            }
        }

        scm {
            connection.set("scm:git:git://github.com/openbancor/catalogmx.git")
            developerConnection.set("scm:git:ssh://git@github.com/openbancor/catalogmx.git")
            url.set("https://github.com/openbancor/catalogmx")
        }
    }
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        freeCompilerArgs = listOf("-Xjsr305=strict")
        jvmTarget = System.getenv("JAVA_VERSION")?.let {
            if (it.toInt() >= 17) "17" else "11"
        } ?: "17"
    }
}
