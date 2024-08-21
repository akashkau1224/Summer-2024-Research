from openai import OpenAI
import os


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "key-here"))

docker = ""

basic_system_prompt = """
You are a security researcher, expert in detecting security vulnerabilities. Carefully analyze the given code and API's and only generate
a test case to test if the code violates the given vulnerability.

"""

system_prompt = """
You are a security researcher, expert in detecting security vulnerabilities. Carefully analyze the given code and API's and only generate
a test case to test if the code violates the given vulnerability. Make sure to look at the source method to see what API actually causes the CWE and run that method in testing

First, write a paragraph thinking how you can use these API's to generate this test case for this specific CWE.

Then, write the test case and explain how it can be used.

"""

user = """

Here is one piece of code adopted from docker-commons-plugin, which is a Docker Commons API Plugin for Jenkins. We have identified a potential OS Command Injection vulnerability in this function, ImageName. Can you write a test case that can be use to check if the vulnerability still persists in this function? 

Here is the source method:

public String imageName(@Nonnull String userAndRepo) throws IOException {
        if (userAndRepo == null) {
            throw new IllegalArgumentException("Image name cannot be null.");
        }
        if (url == null) {
            return userAndRepo;
        }
        URL effectiveUrl = getEffectiveUrl();
        StringBuilder s = new StringBuilder(effectiveUrl.getHost());
        if (effectiveUrl.getPort() > 0 ) {
            s.append(':').append(effectiveUrl.getPort());
        }
        if (userAndRepo.startsWith(String.valueOf(s))) {
            return userAndRepo;
        }
        return s.append('/').append(userAndRepo).toString();
    }

API's needed include:

public DockerRegistryEndpoint(String url, String credentialsId)

/**
     * Decorates the repository ID namespace/name (ie. "jenkinsci/workflow-demo") with registry prefix
     * (docker.acme.com:80/jenkinsci/workflow-demo).
     * 
     * @param userAndRepo
     *            the namespace/name part to append to the registry
     * @return the full registry:port/namespace/name string
     * @throws IOException
*/
public String imageName(@NonNull String userAndRepo) throws IOException 
    
Here is an example test case to format off of

@Issue("JENKINS-39181")
@Test(expected = IllegalArgumentException.class)
@WithoutJenkins
public void testParseNullImageName() throws Exception {
    new DockerRegistryEndpoint("http://private-repo:5000/", null).imageName(null);
}

"""

system_response = """
To identify an OS Command Injection vulnerability in this function, we need to test if the input `userAndRepo` can be used to inject malicious commands. OS Command Injection typically occurs when an application constructs a command to execute on the operating system based on user input without proper validation or sanitization. Considering the given code, the potential vulnerability might be in how the `userAndRepo` string is handled and concatenated, which may be leveraged to execute arbitrary commands.

Given that we are dealing with a URL and a string concatenation, we would need to ensure that user input is not being misused to construct a potentially malicious URL. We need to create a test case that simulates a scenario where an attacker might input a malicious string to see if it gets executed or improperly handled.

Here is the test case:

@Test
public void testImageNameWithMaliciousInput() throws Exception {
    // Construct the DockerRegistryEndpoint with a valid URL and credentials
    DockerRegistryEndpoint endpoint = new DockerRegistryEndpoint("http://private-repo:5000/", null);

    // Malicious input attempt to inject OS command
    String maliciousInput = "user/repo; echo injected > /tmp/injected.txt";

    try {
        // Call the imageName method with the malicious input
        String result = endpoint.imageName(maliciousInput);

        // Check if the result contains the malicious part
        // In a real vulnerability, we'd check if the command got executed on the system
        // However, for the sake of this test, we're just checking the string composition
        assertFalse("The result should not contain the injected command", result.contains("echo injected"));

        // Additional checks could be added to ensure no side effects occurred
    } catch (IOException e) {
        // Handle exception if thrown
        fail("IOException should not have been thrown");
    }
}


### Explanation:

1. **Setup**: The test constructs a `DockerRegistryEndpoint` object using a valid URL and null credentials.
2. **Malicious Input**: The test case uses a string (`maliciousInput`) designed to inject a command (`echo injected > /tmp/injected.txt`). This simulates an attacker attempting to execute a command via input.
3. **Method Invocation**: The `imageName` method is called with the malicious input.
4. **Validation**: The test asserts that the result string does not contain the injected command, which would indicate that the input was improperly handled.
5. **Exception Handling**: The test ensures that no `IOException` is thrown unless expected.

This test case checks if the malicious input is improperly incorporated into the result, which would indicate a vulnerability. If the result contains the injected command, it suggests a potential for OS Command Injection.

"""

follow_up = """
The intended behavior is to throw some sort of exception, not remove the injection from the imageName
"""

MODEL = "gpt-4o"
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user},
        {"role": "assistant", "content": system_response},
        {"role": "user", "content": follow_up}
    ],
    temperature=0.7,
)

print(response.choices[0].message.content)