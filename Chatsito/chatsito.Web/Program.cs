using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;
using chatsito.Core;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

// Configure HTTP JSON options to support string to enum conversion
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.Converters.Add(new JsonStringEnumConverter(System.Text.Json.JsonNamingPolicy.CamelCase));
});

const string AllowVsCodeOriginPolicy = "AllowVsCodeExtension";

// Add services to the container.
builder.Services.AddRazorPages();

// Configure CORS for VS Code Extension webviews (which run on vscode-webview:// scheme or localhost)
builder.Services.AddCors(options =>
{
    options.AddPolicy(AllowVsCodeOriginPolicy, policy =>
    {
        policy.SetIsOriginAllowed(origin => true) // allows any origin, including null/webview schemes, without using wildcard
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials(); // supports credentials: 'include'
    });
});

// Configure Data Protection to persist keys so session cookies survive app restarts
builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new System.IO.DirectoryInfo(System.IO.Path.Combine(builder.Environment.ContentRootPath, ".keys")));

// Add session support
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

// Register ModelClient
builder.Services.AddHttpClient<ModelClient>(client =>
{
    client.BaseAddress = new Uri("http://localhost:11434");
    client.Timeout = TimeSpan.FromMinutes(chatsito.Core.Configuration.TimeoutMins);
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

//app.UseHttpsRedirection();

app.UseRouting();

// Enable CORS
app.UseCors(AllowVsCodeOriginPolicy);

app.UseSession(); // Enable session before authorization & routing

app.UseAuthorization();

app.MapStaticAssets();
app.MapRazorPages()
   .WithStaticAssets();

// Expose API endpoints using ApiManager
chatsito.Web.ApiManager.MapApiEndpoints(app);

app.Run();
