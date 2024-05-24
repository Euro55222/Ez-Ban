require 'cgi'
require 'httparty'
require 'json'
require 'nokogiri'
require 'colorize'
require 'net/http'
require 'uri'
require 'thread'

class String
    def magenta;        "\e[35m#{self}\e[0m" end
end

def require_gem(name)
    Gem::Specification.find_by_name(name)
rescue Gem::LoadError
    puts "Gem '#{name}' Is Not Installed. Installing..."
    system("gem install #{name}")
    Gem::Specification.find_by_name(name)
end

required_gems = %w[cgi httparty json nokogiri colorize net-http-persistent]

required_gems.each { |gem| require_gem(gem) }
puts "
████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗   ██████╗  █████╗ ███╗   ██╗
╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝   ██╔══██╗██╔══██╗████╗  ██║
   ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝    ██████╔╝███████║██╔██╗ ██║
   ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗    ██╔══██╗██╔══██║██║╚██╗██║
   ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗██╗██████╔╝██║  ██║██║ ╚████║
   ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
                               GitHub: LeetIDA                                    
".magenta

class IDA
    def initialize
        @proxy_source = nil
        puts "Choose Proxy Source: 1. Local File 2. Online"
        choice = gets.chomp.to_i
        case choice
        when 1
            puts "Enter the path to your local proxy file:"
            @proxy_source = gets.chomp
        when 2
            @proxy_key = nil
            print '[>] Proxy Key '.colorize(:light_yellow)
            @proxy_url = 'https://advanced.name/freeproxy/'
            open_proxy_link
        else
            puts "Invalid choice. Exiting..."
            exit
        end
        print '[?] Username: '.colorize(:light_blue)
        @username = gets.chomp
        @username.delete!('@') if @username[0] == '@' || @username.include?('@')
        @server_log = nil
        @data_json = nil
        admin
    end

    def open_proxy_link
        puts "To Get The Key Enter This URL And solve the captcha ex.(#{@proxy_url}<key>)".colorize(:red)
        print 'Key: '
        @proxy_key = gets.chomp
        @proxy_url += @proxy_key
    rescue
        puts "Failed to open the proxy link. Please manually visit the URL: #{@proxy_url}"
        print 'Key: '
        @proxy_key = gets.chomp
        @proxy_url += @proxy_key
    end

    def admin
        threads = []
        10.times do
            threads << Thread.new { send_request }
        end
        threads.each(&:join)
        _to_json
        output
    end

    def send_request
        headers = {
            'User-Agent' => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 IDA'
        }
        @response = HTTParty.get("https://www.tiktok.com/@#{@username}", headers: headers)
        if @response.code == 403
            handle_forbidden_error
        else
            @server_log = @response.body
        end
    end

    def handle_forbidden_error
        puts "403 Forbidden Error: Your request to TikTok was blocked.".colorize(:red)
        puts "Possible actions to resolve this issue:".colorize(:yellow)
        puts "- Ensure your IP is not blacklisted by TikTok.".colorize(:light_blue)
        puts "- Try using a different IP address or proxy.".colorize(:light_blue)
        puts "- Wait and try again later if TikTok's rate limiting is causing the block.".colorize(:light_blue)
        exit
    end
    
    def _to_json
        begin
            script_tag = Nokogiri::HTML(@response.body).at('script#__UNIVERSAL_DATA_FOR_REHYDRATION__')
            script_text = script_tag.text.strip
            @json_data = JSON.parse(script_text)['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
        rescue StandardError
            puts '[X] Error: Username Not Found.'
            exit
        end
    end
    
    def get_user_id
        begin
            data = @json_data
            data["user"]["id"]
        rescue StandardError
            'Unknown'
        end
    end
    
    def secUid
        begin
            data = @json_data
            data["user"]["secUid"]
        rescue StandardError
            'Unknown'
        end
    end
    
    def generate_report_url
        # URL generation logic remains unchanged
    end

    def output
        report_url = generate_report_url
        tiktok_url = report_url
        max_retries = 3
        retries = 0
        backoff = 1
        proxy_list = if @proxy_source
                       File.readlines(@proxy_source).map(&:chomp)
                     else
                       Net::HTTP.get(URI(@proxy_url)).split("\r\n")
                     end

        proxy_list.each do |proxy|
            Thread.new do
                begin
                    current_time = Time.now.strftime('%H:%M:%S')
                    uri = URI(tiktok_url)
                    req = Net::HTTP::Post.new(uri)
                    http_proxy = "http://#{proxy}"
                    req['proxy'] = http_proxy
                    res = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == 'https', open_timeout: 2, read_timeout: 2) do |http|
                        http.request(req)
                    end
                    puts "[#{current_time}]".colorize(:red) + " #{'Proxy: ' + proxy} Report Sent To #{@username}".colorize(:green)
                    retries = 0 # Reset retries after a successful request
                rescue Net::OpenTimeout => e
                    puts "Attempt #{retries + 1}: Something went wrong: #{e}".colorize(:red)
                    if retries < max_retries
                        retries += 1
                        sleep(backoff)
                        backoff *= 2
                        redo
                    else
                        puts 'Max retries reached. Moving to the next proxy.'.colorize(:red)
                        retries = 0 # Reset retries for the next proxy
                        backoff = 1 # Reset backoff for the next proxy
                    end
                rescue => e
                    puts "Something went wrong: #{e}".colorize(:red)
                    puts 'Press Enter to close the program'.colorize(:red)
                    gets.chomp
                    exit()
                end
            end
        end
    end
end

IDA.new
